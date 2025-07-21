from fastapi import APIRouter, HTTPException

roles_router = APIRouter()

@roles_router.post("/")
def create_role(role_name: str):
    return {"message": f"Role '{role_name}' created successfully"}

@roles_router.get("/")
def list_roles():
    return {"roles": ["Admin", "User"]}

@roles_router.put("/{role_id}")
def update_role(role_id: int, role_name: str):
    return {"message": f"Role '{role_id}' updated to '{role_name}'"}

@roles_router.delete("/{role_id}")
def delete_role(role_id: int):
    return {"message": f"Role '{role_id}' deleted successfully"}