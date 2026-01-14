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
COPY admin_dashboard/ .
COPY .env.local .

EXPOSE 8004

# Comando para iniciar la aplicación: el dashboard usualmente lee de otros servicios, no tiene DB propia usualmente
# Pero si la tuviera, se inicializaría aquí.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8004"]
