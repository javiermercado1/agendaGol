from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/")
def create_role(role_name: str):
    # Lógica para crear un rol
    return {"message": f"Role '{role_name}' created successfully"}

@router.get("/")
def list_roles():
    # Lógica para listar roles
    return {"roles": ["Admin", "User"]}

@router.put("/{role_id}")
def update_role(role_id: int, role_name: str):
    # Lógica para actualizar un rol
    return {"message": f"Role '{role_id}' updated to '{role_name}'"}

@router.delete("/{role_id}")
def delete_role(role_id: int):
    # Lógica para eliminar un rol
    return {"message": f"Role '{role_id}' deleted successfully"}