from fastapi import FastAPI
from app.routes import auth_routes
from app.database import init_db

app = FastAPI(title="Auth Service")

init_db()

app.include_router(auth_routes, prefix="/auth", tags=["Authentication"])

