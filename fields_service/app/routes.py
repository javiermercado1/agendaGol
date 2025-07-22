from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta, time
import requests
import os

from app.database import get_db
from app.models import Field
from app.schemas import FieldCreate, FieldUpdate, FieldResponse, FieldListResponse, FieldAvailability

fields_router = APIRouter()

# URLs de otros servicios
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8000")
ROLES_SERVICE_URL = os.getenv("ROLES_SERVICE_URL", "http://roles_service:8001")
RESERVATIONS_SERVICE_URL = os.getenv("RESERVATIONS_SERVICE_URL", "http://reservations_service:8003")

def verify_admin_permission(auth_header: str):
    """Verificar que el usuario tenga permisos de administrador"""
    try:
        # Verificar token con auth service
        auth_response = requests.get(
            f"{AUTH_SERVICE_URL}/auth/verify",
            headers={"Authorization": auth_header}
        )
        if auth_response.status_code != 200:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        user_data = auth_response.json()
        user_id = user_data.get("user_id")
        
        # Verificar permisos con roles service
        roles_response = requests.get(
            f"{ROLES_SERVICE_URL}/roles/user/{user_id}/permissions",
            headers={"Authorization": auth_header}
        )
        if roles_response.status_code != 200:
            raise HTTPException(status_code=403, detail="Error verificando permisos")
        
        permissions = roles_response.json().get("permissions", [])
        has_admin_permission = any(
            perm.get("resource") == "fields" and perm.get("action") in ["create", "update", "delete", "manage"]
            for perm in permissions
        )
        
        if not has_admin_permission:
            raise HTTPException(status_code=403, detail="Permisos insuficientes")
        
        return user_id
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Error conectando con servicios de autenticación")

@fields_router.post("/", response_model=FieldResponse)
def create_field(
    field: FieldCreate,
    db: Session = Depends(get_db),
    auth_header: str = Depends(lambda request: request.headers.get("Authorization"))
):
    user_id = verify_admin_permission(auth_header)
    
    # Verificar que no exista una cancha con el mismo nombre
    existing_field = db.query(Field).filter(Field.name == field.name).first()
    if existing_field:
        raise HTTPException(status_code=400, detail="Ya existe una cancha con ese nombre")
    
    db_field = Field(
        **field.dict(),
        created_by=user_id
    )
    db.add(db_field)
    db.commit()
    db.refresh(db_field)
    
    return db_field

@fields_router.get("/", response_model=FieldListResponse)
def list_fields(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    is_active: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Field)
    
    if is_active is not None:
        query = query.filter(Field.is_active == is_active)
    
    total = query.count()
    fields = query.offset(skip).limit(limit).all()
    
    return FieldListResponse(
        fields=fields,
        total=total,
        page=skip // limit + 1,
        size=limit
    )

@fields_router.get("/{field_id}", response_model=FieldResponse)
def get_field(field_id: int, db: Session = Depends(get_db)):
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Cancha no encontrada")
    return field

@fields_router.put("/{field_id}", response_model=FieldResponse)
def update_field(
    field_id: int,
    field_update: FieldUpdate,
    db: Session = Depends(get_db),
    auth_header: str = Depends(lambda request: request.headers.get("Authorization"))
):
    verify_admin_permission(auth_header)
    
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Cancha no encontrada")
    
    # Actualizar solo los campos proporcionados
    for key, value in field_update.dict(exclude_unset=True).items():
        setattr(field, key, value)
    
    db.commit()
    db.refresh(field)
    return field

@fields_router.delete("/{field_id}")
def delete_field(
    field_id: int,
    db: Session = Depends(get_db),
    auth_header: str = Depends(lambda request: request.headers.get("Authorization"))
):
    verify_admin_permission(auth_header)
    
    field = db.query(Field).filter(Field.id == field_id).first()
    if not field:
        raise HTTPException(status_code=404, detail="Cancha no encontrada")
    
    # Soft delete - marcar como inactiva
    field.is_active = False
    db.commit()
    
    return {"message": f"Cancha '{field.name}' eliminada exitosamente"}

@fields_router.get("/{field_id}/availability", response_model=FieldAvailability)
def get_field_availability(
    field_id: int,
    date: datetime = Query(..., description="Fecha para verificar disponibilidad (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    field = db.query(Field).filter(Field.id == field_id, Field.is_active == True).first()
    if not field:
        raise HTTPException(status_code=404, detail="Cancha no encontrada")
    
    # Verificar que la fecha no sea muy lejana (máximo 30 días)
    max_date = datetime.now() + timedelta(days=30)
    if date.date() > max_date.date():
        raise HTTPException(status_code=400, detail="No se pueden hacer reservas con más de 30 días de anticipación")
    
    # Generar horarios disponibles (de 10 AM a 10 PM, en bloques de 1 hora)
    available_hours = []
    current_hour = field.opening_time.hour
    closing_hour = field.closing_time.hour
    
    try:
        # Obtener reservas existentes para esa fecha
        reservations_response = requests.get(
            f"{RESERVATIONS_SERVICE_URL}/reservations/field/{field_id}/date/{date.date()}"
        )
        reserved_hours = []
        if reservations_response.status_code == 200:
            reservations = reservations_response.json()
            for reservation in reservations:
                if reservation.get("status") == "confirmada":
                    start_time = datetime.fromisoformat(reservation["start_time"]).hour
                    duration = reservation["duration_hours"]
                    for hour in range(start_time, start_time + duration):
                        reserved_hours.append(hour)
    except requests.exceptions.RequestException:
        # Si el servicio de reservas no está disponible, asumir que no hay reservas
        reserved_hours = []
    
    # Generar lista de horarios disponibles
    while current_hour < closing_hour:
        if current_hour not in reserved_hours:
            available_hours.append(f"{current_hour:02d}:00")
        current_hour += 1
    
    return FieldAvailability(
        field_id=field_id,
        date=date,
        available_hours=available_hours
    )