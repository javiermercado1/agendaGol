# Usa una imagen base de Python
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY .env.local .

COPY roles_service/ .

# Copiar script de inicialización
COPY roles_service/init_roles.py .

EXPOSE 8001

# Crear un script para inicializar las tablas, roles y permisos
RUN echo "import time\ntime.sleep(10)\nfrom app.database import init_db\ninit_db()" > init_db.py

# Comando para iniciar la aplicación
CMD ["sh", "-c", "python init_db.py && python init_roles.py && uvicorn app.main:app --host 0.0.0.0 --port 8001"]
