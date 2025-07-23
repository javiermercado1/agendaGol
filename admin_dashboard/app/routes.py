from fastapi import APIRouter, HTTPException, Depends, Query, Request
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import requests
import os

dashboard_router = APIRouter()

# URLs de otros servicios
AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")
ROLES_SERVICE_URL = os.getenv("ROLES_SERVICE_URL")
FIELDS_SERVICE_URL = os.getenv("FIELDS_SERVICE_URL")
RESERVATIONS_SERVICE_URL = os.getenv("RESERVATIONS_SERVICE_URL")
FIELDS_SERVICE_URL = os.getenv("FIELDS_SERVICE_URL")
RESERVATIONS_SERVICE_URL = os.getenv("RESERVATIONS_SERVICE_URL")

def verify_admin_permission(auth_header: str):
    """Verificar que el usuario tenga permisos de administrador"""
    if not auth_header:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
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
        """ roles_response = requests.get(
            f"{ROLES_SERVICE_URL}/roles/user/{user_id}/permissions",
            headers={"Authorization": auth_header}
        )
        if roles_response.status_code != 200:
            raise HTTPException(status_code=403, detail="Error verificando permisos")
        
        permissions = roles_response.json().get("permissions", [])
        has_admin_permission = any(
            perm.get("resource") == "dashboard" and perm.get("action") in ["view", "manage"]
            for perm in permissions
        ) or any(
            perm.get("name") == "admin"
            for perm in permissions
        )
        
        if not has_admin_permission:
            raise HTTPException(status_code=403, detail="Permisos insuficientes") """
        
        return user_id
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Error conectando con servicios de autenticación")

def get_service_data(url: str, auth_header: str = None) -> Dict[str, Any]:
    """Obtener datos de un servicio específico"""
    try:
        headers = {"Authorization": auth_header} if auth_header else {}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.json()
        return {}
    except requests.exceptions.RequestException:
        return {}

@dashboard_router.get("/stats")
def get_dashboard_statistics(
    request: Request = None
):
    """Obtener estadísticas generales del dashboard"""
    auth_header = None
    if request:
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    
    verify_admin_permission(auth_header)
    
    # Obtener estadísticas de usuarios
    users_data = get_service_data(f"{AUTH_SERVICE_URL}/auth/users/stats", auth_header)
    total_users = users_data.get("total_users", 0)
    
    # Obtener estadísticas de canchas
    fields_data = get_service_data(f"{FIELDS_SERVICE_URL}/fields?limit=1000")
    total_fields = fields_data.get("total", 0)
    active_fields = len([f for f in fields_data.get("fields", []) if f.get("is_active", False)])
    
    # Obtener estadísticas de reservas
    reservations_stats = get_service_data(f"{RESERVATIONS_SERVICE_URL}/reservations/stats", auth_header)
    
    # Obtener reservas recientes
    recent_reservations = get_service_data(
        f"{RESERVATIONS_SERVICE_URL}/reservations?limit=10&status=confirmada",
        auth_header
    )
    
    recent_cancelled = get_service_data(
        f"{RESERVATIONS_SERVICE_URL}/reservations?limit=10&status=cancelada",
        auth_header
    )
    
    return {
        "general_stats": {
            "total_users": total_users,
            "total_fields": total_fields,
            "active_fields": active_fields,
            "total_reservations": reservations_stats.get("total_reservations", 0),
            "active_reservations": reservations_stats.get("active_reservations", 0),
            "cancelled_reservations": reservations_stats.get("cancelled_reservations", 0),
            "reservations_today": reservations_stats.get("reservations_today", 0),
            "total_revenue": reservations_stats.get("total_revenue", 0.0)
        },
        "recent_activity": {
            "latest_reservations": recent_reservations.get("reservations", [])[:5],
            "latest_cancelled": recent_cancelled.get("reservations", [])[:5]
        },
        "last_updated": datetime.now().isoformat()
    }

@dashboard_router.get("/users")
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    request: Request = None
):
    """Listar usuarios registrados con filtros"""
    auth_header = None
    if request:
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    
    verify_admin_permission(auth_header)
    
    # Construir parámetros de consulta
    params = {
        "skip": skip,
        "limit": limit
    }
    if role:
        params["role"] = role
    if is_active is not None:
        params["is_active"] = is_active
    
    try:
        # Obtener usuarios del servicio de autenticación
        response = requests.get(
            f"{AUTH_SERVICE_URL}/auth/users",
            params=params,
            headers={"Authorization": auth_header},
            timeout=10
        )
        
        if response.status_code == 200:
            users_data = response.json()
            
            # Enriquecer con información de roles para cada usuario
            for user in users_data.get("users", []):
                user_id = user.get("id")
                roles_data = get_service_data(
                    f"{ROLES_SERVICE_URL}/roles/user/{user_id}",
                    auth_header
                )
                user["roles"] = roles_data.get("roles", [])
            
            return users_data
        else:
            raise HTTPException(status_code=response.status_code, detail="Error obteniendo usuarios")
    
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Error conectando con servicio de usuarios")

@dashboard_router.get("/reservations")
def get_reservations_overview(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    field_id: Optional[int] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    request: Request = None
):
    """Obtener vista general de reservas para el dashboard"""
    auth_header = None
    if request:
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    
    verify_admin_permission(auth_header)
    
    # Construir parámetros de consulta
    params = {
        "skip": skip,
        "limit": limit
    }
    if status:
        params["status"] = status
    if field_id:
        params["field_id"] = field_id
    
    try:
        response = requests.get(
            f"{RESERVATIONS_SERVICE_URL}/reservations",
            params=params,
            headers={"Authorization": auth_header},
            timeout=10
        )
        
        if response.status_code == 200:
            reservations_data = response.json()
            
            # Enriquecer con información del usuario para cada reserva
            for reservation in reservations_data.get("reservations", []):
                user_id = reservation.get("user_id")
                user_data = get_service_data(
                    f"{AUTH_SERVICE_URL}/auth/user/{user_id}",
                    auth_header
                )
                reservation["user_info"] = {
                    "name": user_data.get("name", "Usuario desconocido"),
                    "email": user_data.get("email", "")
                }
            
            return reservations_data
        else:
            raise HTTPException(status_code=response.status_code, detail="Error obteniendo reservas")
    
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Error conectando con servicio de reservas")

@dashboard_router.get("/fields/stats")
def get_fields_statistics(
    request: Request = None
):
    """Obtener estadísticas detalladas de las canchas"""
    auth_header = None
    if request:
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    
    verify_admin_permission(auth_header)
    
    # Obtener todas las canchas
    fields_data = get_service_data(f"{FIELDS_SERVICE_URL}/fields?limit=1000")
    fields = fields_data.get("fields", [])
    
    field_stats = []
    
    for field in fields:
        field_id = field.get("id")
        
        # Obtener reservas para esta cancha
        reservations_data = get_service_data(
            f"{RESERVATIONS_SERVICE_URL}/reservations?field_id={field_id}&limit=1000",
            auth_header
        )
        
        reservations = reservations_data.get("reservations", [])
        
        # Calcular estadísticas
        total_reservations = len(reservations)
        confirmed_reservations = len([r for r in reservations if r.get("status") == "confirmada"])
        cancelled_reservations = len([r for r in reservations if r.get("status") == "cancelada"])
        total_revenue = sum(r.get("total_price", 0) for r in reservations if r.get("status") == "confirmada")
        
        # Reservas de esta semana
        week_ago = datetime.now() - timedelta(days=7)
        weekly_reservations = len([
            r for r in reservations 
            if datetime.fromisoformat(r.get("created_at", "").replace("Z", "")) > week_ago
        ])
        
        field_stats.append({
            "field_id": field_id,
            "field_name": field.get("name"),
            "field_location": field.get("location"),
            "is_active": field.get("is_active"),
            "total_reservations": total_reservations,
            "confirmed_reservations": confirmed_reservations,
            "cancelled_reservations": cancelled_reservations,
            "weekly_reservations": weekly_reservations,
            "total_revenue": total_revenue,
            "average_price": field.get("price_per_hour", 0),
            "capacity": field.get("capacity", 0)
        })
    
    # Ordenar por total de reservas descendente
    field_stats.sort(key=lambda x: x["total_reservations"], reverse=True)
    
    return {
        "fields_statistics": field_stats,
        "summary": {
            "total_fields": len(fields),
            "active_fields": len([f for f in fields if f.get("is_active", False)]),
            "total_revenue": sum(f["total_revenue"] for f in field_stats),
            "most_popular_field": field_stats[0] if field_stats else None
        }
    }

@dashboard_router.get("/revenue/daily")
def get_daily_revenue(
    days: int = Query(30, ge=1, le=365),
    request: Request = None
):
    """Obtener ingresos diarios de los últimos N días"""
    auth_header = None
    if request:
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    
    verify_admin_permission(auth_header)
    
    # Obtener todas las reservas confirmadas de los últimos días
    date_from = datetime.now() - timedelta(days=days)
    
    try:
        response = requests.get(
            f"{RESERVATIONS_SERVICE_URL}/reservations?status=confirmada&limit=10000",
            headers={"Authorization": auth_header},
            timeout=15
        )
        
        if response.status_code == 200:
            reservations = response.json().get("reservations", [])
            
            # Agrupar por día
            daily_revenue = {}
            for i in range(days):
                date = (datetime.now() - timedelta(days=i)).date()
                daily_revenue[date.isoformat()] = 0
            
            for reservation in reservations:
                created_date = datetime.fromisoformat(
                    reservation.get("created_at", "").replace("Z", "")
                ).date()
                
                if created_date >= date_from.date():
                    date_key = created_date.isoformat()
                    if date_key in daily_revenue:
                        daily_revenue[date_key] += reservation.get("total_price", 0)
            
            return {
                "daily_revenue": daily_revenue,
                "period_days": days,
                "total_period_revenue": sum(daily_revenue.values())
            }
        else:
            raise HTTPException(status_code=response.status_code, detail="Error obteniendo datos de ingresos")
    
    except requests.exceptions.RequestException:
        raise HTTPException(status_code=503, detail="Error conectando con servicio de reservas")

@dashboard_router.get("/health-check")
def dashboard_health_check(
    request: Request = None
):
    """Verificar el estado de todos los servicios"""
    auth_header = None
    if request:
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization")
    
    verify_admin_permission(auth_header)
    
    services = [
        ("Auth Service", f"{AUTH_SERVICE_URL}/health"),
        ("Roles Service", f"{ROLES_SERVICE_URL}/health"),
        ("Fields Service", f"{FIELDS_SERVICE_URL}/health"),
        ("Reservations Service", f"{RESERVATIONS_SERVICE_URL}/health")
    ]
    
    service_status = {}
    
    for service_name, health_url in services:
        try:
            response = requests.get(health_url, timeout=5)
            service_status[service_name] = {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response.elapsed.total_seconds(),
                "status_code": response.status_code
            }
        except requests.exceptions.RequestException as e:
            service_status[service_name] = {
                "status": "error",
                "error": str(e),
                "response_time": None,
                "status_code": None
            }
    
    overall_status = "healthy" if all(
        s["status"] == "healthy" for s in service_status.values()
    ) else "degraded"
    
    return {
        "overall_status": overall_status,
        "services": service_status,
        "checked_at": datetime.now().isoformat()
    }