# Usa una imagen base de Python
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY .env.local .

COPY auth_service/ .

EXPOSE 8000

# Crear un script para inicializar las tablas y luego ejecutar uvicorn
RUN echo "from app.database import Base, engine\nfrom app.models import User\nBase.metadata.create_all(bind=engine)" > init_db.py

# Comando para iniciar la aplicación
CMD ["sh", "-c", "python init_db.py && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
