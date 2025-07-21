from fastapi import APIRouter

dashboard_router = APIRouter()

@dashboard_router.get("/stats")
def get_statistics():
    # Lógica para obtener estadísticas
    return {"stats": {"active_reservations": 10, "canceled_reservations": 2}}

@dashboard_router.get("/users")
def list_users():
    # Lógica para listar usuarios
    return {"users": [{"id": 1, "name": "John Doe", "role": "Admin"}]}