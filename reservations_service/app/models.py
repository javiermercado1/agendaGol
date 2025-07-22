from sqlalchemy import Column, Integer, String, DateTime, Enum, Float, Text
from sqlalchemy.sql import func
from app.database import Base
import enum

class ReservationStatus(enum.Enum):
    CONFIRMADA = "confirmada"
    CANCELADA = "cancelada"

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)  # ID del usuario que hace la reserva
    field_id = Column(Integer, nullable=False, index=True)  # ID de la cancha
    
    # Información de la reserva
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False)
    duration_hours = Column(Integer, nullable=False)  
    
    # Información de la cancha (cache para evitar consultas)
    field_name = Column(String, nullable=False)
    field_location = Column(String, nullable=False)
    total_price = Column(Float, nullable=False)
    
    # Estado y metadatos
    status = Column(Enum(ReservationStatus), default=ReservationStatus.CONFIRMADA, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    cancelled_at = Column(DateTime, nullable=True)
    cancelled_by = Column(Integer, nullable=True)  # ID del usuario que canceló

    def __repr__(self):
        return f"<Reservation(id={self.id}, user_id={self.user_id}, field_id={self.field_id}, status={self.status.value})>"

    @property
    def is_active(self):
        """Verifica si la reserva está activa (confirmada y no ha pasado)"""
        from datetime import datetime
        return self.status == ReservationStatus.CONFIRMADA and self.start_time > datetime.now()

    @property
    def can_be_cancelled(self):
        """Verifica si la reserva puede ser cancelada (está confirmada y no ha empezado)"""
        from datetime import datetime
        return self.status == ReservationStatus.CONFIRMADA and self.start_time > datetime.now()
