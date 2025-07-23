from pydantic import BaseModel, validator, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class ReservationStatusEnum(str, Enum):
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"

class ReservationBase(BaseModel):
    field_id: int
    start_time: datetime
    duration_hours: int
    notes: Optional[str] = None

    @validator('duration_hours')
    def duration_must_be_valid(cls, v):
        if v not in [1, 2]:
            raise ValueError('La duración debe ser de 1 o 2 horas')
        return v

    @validator('start_time')
    def start_time_validation(cls, v):
        # Verificar que no sea en el pasado
        if v <= datetime.now():
            raise ValueError('La fecha de reserva debe ser futura')
        
        # Verificar que no sea más de 30 días en el futuro
        from datetime import timedelta
        max_date = datetime.now() + timedelta(days=30)
        if v > max_date:
            raise ValueError('No se pueden hacer reservas con más de 30 días de anticipación')
        
        # Verificar que esté en horario válido (10 AM - 10 PM)
        hour = v.hour
        if hour < 10 or hour >= 22:
            raise ValueError('Las reservas solo pueden ser entre 10:00 AM y 10:00 PM')
        
        # Verificar que sea en punto (exactamente en la hora)
        if v.minute != 0 or v.second != 0:
            raise ValueError('Las reservas deben ser exactamente en la hora (ej: 14:00, 15:00)')
        
        return v

class ReservationCreate(ReservationBase):
    pass

class ReservationUpdate(BaseModel):
    start_time: Optional[datetime] = None
    duration_hours: Optional[int] = None
    notes: Optional[str] = None

    @validator('duration_hours')
    def duration_must_be_valid(cls, v):
        if v is not None and v not in [1, 2]:
            raise ValueError('La duración debe ser de 1 o 2 horas')
        return v

class ReservationResponse(ReservationBase):
    id: int
    user_id: int
    field_name: str
    field_location: str
    total_price: float
    status: ReservationStatusEnum
    end_time: datetime
    created_at: datetime
    updated_at: datetime
    cancelled_at: Optional[datetime] = None
    cancelled_by: Optional[int] = None

    class Config:
        from_attributes = True

    @validator('status', pre=True)
    def convert_status_enum(cls, v):
        if hasattr(v, 'value'):  
            return v.value
        return v

class ReservationListResponse(BaseModel):
    reservations: list[ReservationResponse]
    total: int
    page: int
    size: int

class ReservationCancelRequest(BaseModel):
    reason: Optional[str] = None

class ReservationStatsResponse(BaseModel):
    total_reservations: int
    active_reservations: int
    cancelled_reservations: int
    reservations_today: int
    total_revenue: float
