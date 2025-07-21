from fastapi import APIRouter, HTTPException

fields_router = APIRouter()

@fields_router.post("/")
def create_field(name: str, location: str, capacity: int, price_per_hour: float):
    return {"message": f"Field '{name}' created successfully"}

@fields_router.get("/")
def list_fields():
    return {"fields": [{"name": "Field 1", "location": "City Center"}]}

@fields_router.get("/{field_id}")
def get_field(field_id: int):
    return {"field": {"id": field_id, "name": "Field 1"}}

@fields_router.put("/{field_id}")
def update_field(field_id: int, name: str, location: str, capacity: int, price_per_hour: float):

    return {"message": f"Field '{field_id}' updated successfully"}

@fields_router.delete("/{field_id}")
def delete_field(field_id: int):

    return {"message": f"Field '{field_id}' deleted successfully"}