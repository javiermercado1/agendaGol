from fastapi import FastAPI
from app.routes import auth_routes

app = FastAPI(title="Auth Service")

app.include_router(auth_routes, prefix="/auth", tags=["Authentication"])

