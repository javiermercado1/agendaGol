from app.database import SessionLocal, init_db
from app.models import Field
from datetime import time

def setup_sample_fields():
    init_db()
    db = SessionLocal()
    
    try:
        # Crear canchas de ejemplo si no existen
        sample_fields = [
            {
                "name": "Cancha Principal",
                "location": "Centro Deportivo Norte",
                "capacity": 22,
                "price_per_hour": 50.0,
                "description": "Cancha de fútbol 11 con césped sintético de última generación",
                "opening_time": time(10, 0),
                "closing_time": time(22, 0),
                "is_active": True
            },
            {
                "name": "Cancha Lateral A",
                "location": "Centro Deportivo Norte",
                "capacity": 14,
                "price_per_hour": 35.0,
                "description": "Cancha de fútbol 7 ideal para entrenamientos",
                "opening_time": time(10, 0),
                "closing_time": time(22, 0),
                "is_active": True
            },
            {
                "name": "Cancha Sur",
                "location": "Complejo Deportivo Sur",
                "capacity": 22,
                "price_per_hour": 45.0,
                "description": "Cancha de fútbol 11 con iluminación LED",
                "opening_time": time(10, 0),
                "closing_time": time(22, 0),
                "is_active": True
            },
            {
                "name": "Cancha Lateral B",
                "location": "Centro Deportivo Norte",
                "capacity": 10,
                "price_per_hour": 30.0,
                "description": "Cancha de fútbol 5 para partidos rápidos",
                "opening_time": time(10, 0),
                "closing_time": time(22, 0),
                "is_active": True
            }
        ]
        
        for field_data in sample_fields:
            existing_field = db.query(Field).filter(Field.name == field_data["name"]).first()
            if not existing_field:
                field = Field(**field_data)
                db.add(field)
                print(f"Creada cancha: {field_data['name']}")
        
        db.commit()
        print("✅ Canchas de ejemplo creadas exitosamente")
        
    except Exception as e:
        print(f"❌ Error creando canchas: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_sample_fields()
