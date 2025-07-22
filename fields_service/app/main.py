from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import fields_router
from app.database import init_db

app = FastAPI(title="Fields Management Service")

# Inicializar base de datos
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

app.include_router(fields_router, prefix="/fields", tags=["Fields"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "fields_service"}