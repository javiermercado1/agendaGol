from fastapi import APIRouter

router = APIRouter()

@router.get("/stats")
def get_statistics():
    # Lógica para obtener estadísticas
    return {"stats": {"active_reservations": 10, "canceled_reservations": 2}}

@router.get("/users")
def list_users():
    # Lógica para listar usuarios
    return {"users": [{"id": 1, "name": "John Doe", "role": "Admin"}]}