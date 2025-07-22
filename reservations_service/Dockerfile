FROM python:3.12-slim

# Instalar cliente de PostgreSQL
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY .env.local .

COPY reservations_service/ .

EXPOSE 8003

# Crear script de espera para la base de datos
RUN echo '#!/bin/bash\nset -e\nuntil pg_isready -h db -p 5432 -U postgres; do\n  echo "Waiting for database..."\n  sleep 2\ndone\necho "Database is ready!"' > wait-for-db.sh
RUN chmod +x wait-for-db.sh

CMD ["sh", "-c", "./wait-for-db.sh && uvicorn app.main:app --host 0.0.0.0 --port 8003"]