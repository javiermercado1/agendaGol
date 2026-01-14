# Usa una imagen base de Python
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app

# Instalar dependencias del sistema mínimas
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código del servicio
COPY roles_service/ .
COPY .env.local .

EXPOSE 8001

# Comando para iniciar la aplicación: asegura inicialización de DB, roles y arranca uvicorn
CMD ["sh", "-c", "python app/init_db.py && python init_roles.py && uvicorn app.main:app --host 0.0.0.0 --port 8001"]
