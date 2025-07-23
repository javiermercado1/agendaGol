from fastapi import APIRouter, HTTPException, Depends, Query, BackgroundTasks, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List, Optional
from datetime import datetime, timedelta, date, time
import requests
import os

from app.database import get_db
from app.models import Reservation, ReservationStatus
from app.schemas import (
    ReservationCreate, ReservationUpdate, ReservationResponse, 
    ReservationListResponse, ReservationCancelRequest, ReservationStatsResponse
)
from app.email_service import EmailService

reservations_router = APIRouter()

# URLs de otros servicios
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")
ROLES_SERVICE_URL = os.getenv("ROLES_SERVICE_URL")
FIELDS_SERVICE_URL = os.getenv("FIELDS_SERVICE_URL")

email_service = EmailService()

def get_current_user(auth_header: str):
    """Obtener información del usuario actual"""
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    try:
        auth_response = requests.get(
            f"{AUTH_SERVICE_URL}/auth/verify",
            headers={"Authorization": auth_header}
        )
        if auth_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        return auth_response.json()
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Error conectando con servicio de autenticación")

def check_admin_permission(user_id: int, auth_header: str) -> bool:
    """Verificar si el usuario tiene permisos de administrador"""
    try:
        print(f"DEBUG - Checking admin permissions for user_id: {user_id}")
        print(f"DEBUG - ROLES_SERVICE_URL: {ROLES_SERVICE_URL}")
        
        roles_response = requests.get(
            f"{ROLES_SERVICE_URL}/roles/user/{user_id}/permissions",
            headers={"Authorization": auth_header}
        )
        
        print(f"DEBUG - Roles service response status: {roles_response.status_code}")
        
        if roles_response.status_code != 200:
            print(f"DEBUG - Roles service error: {roles_response.text}")
            return False
        
        permissions = roles_response.json().get("permissions", [])
        print(f"DEBUG - User permissions: {permissions}")
        
        is_admin = any(
            perm.get("resource") == "reservations" and perm.get("action") in ["view_all", "manage"]
            for perm in permissions
        )
        
        print(f"DEBUG - User is admin: {is_admin}")
        return is_admin
        
    except requests.exceptions.RequestException as e:
        print(f"DEBUG - Request exception in check_admin_permission: {e}")
        return False

def get_field_info(field_id: int):
    """Obtener información de la cancha"""
    try:
        field_response = requests.get(f"{FIELDS_SERVICE_URL}/fields/{field_id}")
        if field_response.status_code != 200:
            raise HTTPException(status_code=404, detail="Cancha no encontrada")
        
        return field_response.json()
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Error conectando con servicio de canchas")

def get_user_email(user_id: int, auth_header: str):
    """Obtener email del usuario"""
    try:
        user_response = requests.get(
            f"{AUTH_SERVICE_URL}/auth/user/{user_id}",
            headers={"Authorization": auth_header}
        )
        if user_response.status_code == 200:
            return user_response.json().get("email")
    except requests.exceptions.RequestException:
        pass
    return None

def parse_time_field(time_value):
    """Convert time field to datetime.time object"""
    from datetime import time
    
    if time_value is None:
        return None
    
    if isinstance(time_value, str):
        try:
            # Handle format "HH:MM" or "HH:MM:SS"
            time_parts = time_value.split(":")
            hour = int(time_parts[0])
            minute = int(time_parts[1]) if len(time_parts) > 1 else 0
            second = int(time_parts[2]) if len(time_parts) > 2 else 0
            return time(hour, minute, second)
        except (ValueError, IndexError):
            return None
    
    # If it's already a time object, return it
    if hasattr(time_value, 'hour'):
        return time_value
    
    return None

def send_reservation_email(reservation: Reservation, action: str, auth_header: str, reason: str = None):
    """Enviar email de notificación de reserva"""
    try:
        user_email = get_user_email(reservation.user_id, auth_header)
        if not user_email:
            return
        
        reservation_data = {
            "id": reservation.id,
            "field_name": reservation.field_name,
            "field_location": reservation.field_location,
            "start_time": reservation.start_time.strftime("%d/%m/%Y %H:%M"),
            "duration_hours": reservation.duration_hours,
            "total_price": reservation.total_price
        }
        
        if action == "create":
            email_service.send_reservation_confirmation(user_email, reservation_data)
        elif action == "cancel":
            email_service.send_reservation_cancellation(user_email, reservation_data, reason)
    except Exception as e:
        print(f"Error enviando email: {e}")

@reservations_router.post("/", response_model=ReservationResponse)
def create_reservation(
    reservation: ReservationCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    request: Request = None
):
    auth_header = None
    if request:
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    
    user_data = get_current_user(auth_header)
    user_id = user_data.get("user_id")
    
    # Obtener información de la cancha
    field_info = get_field_info(reservation.field_id)
    
    # Verificar que la cancha esté activa
    if not field_info.get("is_active"):
        raise HTTPException(status_code=400, detail="La cancha no está disponible")
    
    # Calcular hora de fin
    end_time = reservation.start_time + timedelta(hours=reservation.duration_hours)
    
    # Verificar que no haya conflictos de horario
    existing_reservation = db.query(Reservation).filter(
        and_(
            Reservation.field_id == reservation.field_id,
            Reservation.status == ReservationStatus.CONFIRMADA,
            Reservation.start_time < end_time,
            Reservation.end_time > reservation.start_time
        )
    ).first()
    
    if existing_reservation:
        raise HTTPException(
            status_code=400, 
            detail="Ya existe una reserva confirmada en ese horario"
        )
    
    # Verificar que la hora esté dentro del horario de la cancha
    opening_time = parse_time_field(field_info.get("opening_time")) or time(10, 0)
    closing_time = parse_time_field(field_info.get("closing_time")) or time(22, 0)
    
    field_opening = datetime.combine(reservation.start_time.date(), opening_time)
    field_closing = datetime.combine(reservation.start_time.date(), closing_time)
    
    if reservation.start_time < field_opening or end_time > field_closing:
        raise HTTPException(
            status_code=400,
            detail=f"La reserva debe estar entre {opening_time.strftime('%H:%M')} y {closing_time.strftime('%H:%M')}"
        )
    
    # Calcular precio total
    total_price = field_info.get("price_per_hour", 0) * reservation.duration_hours
    
    # Crear la reserva
    db_reservation = Reservation(
        user_id=user_id,
        field_id=reservation.field_id,
        start_time=reservation.start_time,
        end_time=end_time,
        duration_hours=reservation.duration_hours,
        field_name=field_info.get("name"),
        field_location=field_info.get("location"),
        total_price=total_price,
        notes=reservation.notes,
        status=ReservationStatus.CONFIRMADA
    )
    
    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)
    
    # Enviar email de confirmación en background
    background_tasks.add_task(send_reservation_email, db_reservation, "create", auth_header)
    
    return db_reservation

@reservations_router.get("/", response_model=ReservationListResponse)
def list_reservations(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    field_id: Optional[int] = Query(None),
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    request: Request = None
):
    auth_header = None
    if request:
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    
    user_data = get_current_user(auth_header)
    current_user_id = user_data.get("user_id")
    
    is_admin_from_auth = user_data.get("is_admin", False)
    is_admin_from_roles = check_admin_permission(current_user_id, auth_header)
    
    # Si roles service falla, usar el is_admin del auth service
    is_admin = is_admin_from_roles or is_admin_from_auth
    
    # DEBUG: Agregar logging
    print(f"DEBUG - User ID: {current_user_id}")
    print(f"DEBUG - Is Admin: {is_admin}")
    print(f"DEBUG - Status filter: {status}")
    print(f"DEBUG - Field ID filter: {field_id}")
    
    query = db.query(Reservation)
    
    if not is_admin:
        # Usuario normal solo ve sus reservas
        query = query.filter(Reservation.user_id == current_user_id)
        print(f"DEBUG - Non-admin user, filtering by user_id: {current_user_id}")
    else:
        print("DEBUG - Admin user, showing all reservations")
    
    if status:
        try:
            status_enum = ReservationStatus(status)
            query = query.filter(Reservation.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Estado de reserva inválido")
    
    if field_id:
        query = query.filter(Reservation.field_id == field_id)
    
    # Ordenar por fecha de creación descendente
    query = query.order_by(Reservation.created_at.desc())
    
    total = query.count()
    reservations = query.offset(skip).limit(limit).all()
    
    print(f"DEBUG - Total reservations found: {total}")
    print(f"DEBUG - Reservations returned: {len(reservations)}")
    
    return ReservationListResponse(
        reservations=reservations,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@reservations_router.get("/my", response_model=ReservationListResponse)
def get_my_reservations(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    request: Request = None
):
    auth_header = None
    if request:
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    
    user_data = get_current_user(auth_header)
    user_id = user_data.get("user_id")
    
    query = db.query(Reservation).filter(Reservation.user_id == user_id)
    
    if status:
        try:
            status_enum = ReservationStatus(status)
            query = query.filter(Reservation.status == status_enum)
        except ValueError:
            raise HTTPException(status_code=400, detail="Estado de reserva inválido")
    
    query = query.order_by(Reservation.created_at.desc())
    
    total = query.count()
    reservations = query.offset(skip).limit(limit).all()
    
    return ReservationListResponse(
        reservations=reservations,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@reservations_router.get("/{reservation_id}", response_model=ReservationResponse)
def get_reservation(
    reservation_id: int,
    db: Session = Depends(get_db),
    request: Request = None
):
    auth_header = None
    if request:
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    
    user_data = get_current_user(auth_header)
    current_user_id = user_data.get("user_id")
    
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    
    # Verificar permisos - admin puede ver todas, usuario solo las suyas
    is_admin = check_admin_permission(current_user_id, auth_header)
    if not is_admin and reservation.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="No tienes permisos para ver esta reserva")
    
    return reservation

@reservations_router.put("/{reservation_id}", response_model=ReservationResponse)
def update_reservation(
    reservation_id: int,
    reservation_update: ReservationUpdate,
    db: Session = Depends(get_db),
    request: Request = None
):
    auth_header = None
    if request:
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    
    user_data = get_current_user(auth_header)
    current_user_id = user_data.get("user_id")
    
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    
    # Solo el dueño de la reserva puede editarla
    if reservation.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="No tienes permisos para editar esta reserva")
    
    # Solo se pueden editar reservas confirmadas y futuras
    if not reservation.can_be_cancelled:
        raise HTTPException(status_code=400, detail="Esta reserva no puede ser modificada")
    
    # Actualizar campos
    update_data = reservation_update.dict(exclude_unset=True)
    
    if "start_time" in update_data or "duration_hours" in update_data:
        # Si se cambia la hora o duración, recalcular
        new_start_time = update_data.get("start_time", reservation.start_time)
        new_duration = update_data.get("duration_hours", reservation.duration_hours)
        new_end_time = new_start_time + timedelta(hours=new_duration)
        
        # Verificar conflictos (excluyendo la reserva actual)
        conflicting_reservation = db.query(Reservation).filter(
            and_(
                Reservation.field_id == reservation.field_id,
                Reservation.status == ReservationStatus.CONFIRMADA,
                Reservation.id != reservation_id,
                Reservation.start_time < new_end_time,
                Reservation.end_time > new_start_time
            )
        ).first()
        
        if conflicting_reservation:
            raise HTTPException(
                status_code=400,
                detail="Ya existe una reserva confirmada en ese horario"
            )
        
        # Obtener info de cancha y recalcular precio si cambió la duración
        if "duration_hours" in update_data:
            field_info = get_field_info(reservation.field_id)
            reservation.total_price = field_info.get("price_per_hour", 0) * new_duration
        
        reservation.end_time = new_end_time
    
    for key, value in update_data.items():
        setattr(reservation, key, value)
    
    db.commit()
    db.refresh(reservation)
    
    return reservation

@reservations_router.post("/{reservation_id}/cancel")
def cancel_reservation(
    reservation_id: int,
    cancel_request: ReservationCancelRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    request: Request = None
):
    auth_header = None
    if request:
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    
    user_data = get_current_user(auth_header)
    current_user_id = user_data.get("user_id")
    
    reservation = db.query(Reservation).filter(Reservation.id == reservation_id).first()
    if not reservation:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    
    # Verificar permisos - admin puede cancelar cualquiera, usuario solo las suyas
    is_admin = check_admin_permission(current_user_id, auth_header)
    if not is_admin and reservation.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="No tienes permisos para cancelar esta reserva")
    
    # Verificar que se pueda cancelar
    if not reservation.can_be_cancelled:
        raise HTTPException(status_code=400, detail="Esta reserva no puede ser cancelada")
    
    # Cancelar la reserva
    reservation.status = ReservationStatus.CANCELADA
    reservation.cancelled_at = datetime.now()
    reservation.cancelled_by = current_user_id
    if cancel_request.reason:
        reservation.notes = f"{reservation.notes or ''}\nCancelación: {cancel_request.reason}".strip()
    
    db.commit()
    db.refresh(reservation)
    
    # Enviar email de cancelación en background
    background_tasks.add_task(
        send_reservation_email, 
        reservation, 
        "cancel", 
        auth_header, 
        cancel_request.reason
    )
    
    return {"message": "Reserva cancelada exitosamente"}

# Endpoints para el dashboard y estadísticas

@reservations_router.get("/field/{field_id}/date/{date}")
def get_field_reservations_by_date(
    field_id: int,
    date: date,
    db: Session = Depends(get_db)
):
    """Obtener reservas de una cancha en una fecha específica (para verificar disponibilidad)"""
    reservations = db.query(Reservation).filter(
        and_(
            Reservation.field_id == field_id,
            Reservation.status == ReservationStatus.CONFIRMADA,
            func.date(Reservation.start_time) == date
        )
    ).all()
    
    return [
        {
            "id": r.id,
            "start_time": r.start_time.isoformat(),
            "end_time": r.end_time.isoformat(),
            "duration_hours": r.duration_hours,
            "status": r.status.value
        }
        for r in reservations
    ]

@reservations_router.get("/stats/", response_model=ReservationStatsResponse)
def get_reservation_stats(
    db: Session = Depends(get_db),
    request: Request = None
):
    auth_header = None
    if request:
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    
    user_data = get_current_user(auth_header)
    current_user_id = user_data.get("user_id")
    
    # Solo admin puede ver estadísticas generales
    is_admin = check_admin_permission(current_user_id, auth_header)
    if not is_admin:
        raise HTTPException(status_code=403, detail="Permisos insuficientes")
    
    now = datetime.now()
    today_start = datetime.combine(now.date(), datetime.min.time())
    today_end = datetime.combine(now.date(), datetime.max.time())
    
    # Estadísticas básicas
    total_reservations = db.query(Reservation).count()
    active_reservations = db.query(Reservation).filter(
        and_(
            Reservation.status == ReservationStatus.CONFIRMADA,
            Reservation.start_time > now
        )
    ).count()
    cancelled_reservations = db.query(Reservation).filter(
        Reservation.status == ReservationStatus.CANCELADA
    ).count()
    reservations_today = db.query(Reservation).filter(
        and_(
            Reservation.start_time >= today_start,
            Reservation.start_time <= today_end
        )
    ).count()
    
    # Calcular ingresos totales de reservas confirmadas
    total_revenue_result = db.query(func.sum(Reservation.total_price)).filter(
        Reservation.status == ReservationStatus.CONFIRMADA
    ).scalar()
    total_revenue = float(total_revenue_result or 0)
    
    return ReservationStatsResponse(
        total_reservations=total_reservations,
        active_reservations=active_reservations,
        cancelled_reservations=cancelled_reservations,
        reservations_today=reservations_today,
        total_revenue=total_revenue
    )