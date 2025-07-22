from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import reservations_router
from app.database import init_db

app = FastAPI(title="Reservations Management Service")

# Inicializar base de datos
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

app.include_router(reservations_router, prefix="/reservations", tags=["Reservations"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "reservations_service"}