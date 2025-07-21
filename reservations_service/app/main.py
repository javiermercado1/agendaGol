from fastapi import FastAPI
from app.routes import reservations

app = FastAPI(title="Reservations Management Service")

app.include_router(reservations.router, prefix="/reservations", tags=["Reservations"])