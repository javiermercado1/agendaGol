from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.post("/")
def create_reservation(field_id: int, date: str, duration: int):
    # Lógica para crear una reserva
    return {"message": f"Reservation for field '{field_id}' created successfully"}

@router.get("/")
def list_reservations():
    # Lógica para listar reservas
    return {"reservations": [{"field_id": 1, "date": "2023-10-01", "status": "active"}]}

@router.put("/{reservation_id}")
def update_reservation(reservation_id: int, date: str, duration: int):
    # Lógica para actualizar una reserva
    return {"message": f"Reservation '{reservation_id}' updated successfully"}

@router.delete("/{reservation_id}")
def cancel_reservation(reservation_id: int):
    # Lógica para cancelar una reserva
    return {"message": f"Reservation '{reservation_id}' canceled successfully"}