from fastapi import FastAPI
from app.routes import reservations_router

app = FastAPI(title="Reservations Management Service")

app.include_router(reservations_router, prefix="/reservations", tags=["Reservations"])