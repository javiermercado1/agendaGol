from pydantic import BaseModel, validator
from datetime import datetime, time
from typing import Optional

class FieldBase(BaseModel):
    name: str
    location: str
    capacity: int
    price_per_hour: float
    description: Optional[str] = None
    opening_time: Optional[time] = time(10, 0)  
    closing_time: Optional[time] = time(22, 0)  
    is_active: Optional[bool] = True

    @validator('capacity')
    def capacity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('La capacidad debe ser mayor a 0')
        return v

    @validator('price_per_hour')
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError('El precio por hora debe ser mayor a 0')
        return v

    @validator('closing_time')
    def closing_time_after_opening(cls, v, values):
        if 'opening_time' in values and v <= values['opening_time']:
            raise ValueError('La hora de cierre debe ser posterior a la hora de apertura')
        return v

class FieldCreate(FieldBase):
    pass

class FieldUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    price_per_hour: Optional[float] = None
    description: Optional[str] = None
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None
    is_active: Optional[bool] = None

    @validator('capacity')
    def capacity_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('La capacidad debe ser mayor a 0')
        return v

    @validator('price_per_hour')
    def price_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError('El precio por hora debe ser mayor a 0')
        return v

class FieldResponse(FieldBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[int] = None

    class Config:
        from_attributes = True

class FieldAvailability(BaseModel):
    field_id: int
    date: datetime
    available_hours: list[str] 

class FieldListResponse(BaseModel):
    fields: list[FieldResponse]
    total: int
    page: int
    size: int
