from fastapi import APIRouter, HTTPException

reservations_router = APIRouter()

@reservations_router.post("/")
def create_reservation(field_id: int, date: str, duration: int):
    return {"message": f"Reservation for field '{field_id}' created successfully"}

@reservations_router.get("/")
def list_reservations():
    return {"reservations": [{"field_id": 1, "date": "2023-10-01", "status": "active"}]}

@reservations_router.put("/{reservation_id}")
def update_reservation(reservation_id: int, date: str, duration: int):
    return {"message": f"Reservation '{reservation_id}' updated successfully"}

@reservations_router.delete("/{reservation_id}")
def cancel_reservation(reservation_id: int):
    return {"message": f"Reservation '{reservation_id}' canceled successfully"}