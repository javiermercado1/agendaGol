from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Time
from sqlalchemy.sql import func
from app.database import Base

class Field(Base):
    __tablename__ = "fields"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    location = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    price_per_hour = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Horarios de funcionamiento
    opening_time = Column(Time, default="10:00:00")  
    closing_time = Column(Time, default="22:00:00")  
    
    # Metadatos
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by = Column(Integer, nullable=True)  

    def __repr__(self):
        return f"<Field(id={self.id}, name='{self.name}', location='{self.location}')>"

    def is_available_at_time(self, check_time):
        """Verifica si la cancha está disponible en el horario especificado"""
        if not self.is_active:
            return False
        
        # Convertir a time si es datetime
        if hasattr(check_time, 'time'):
            check_time = check_time.time()
        
        return self.opening_time <= check_time <= self.closing_time
