from fastapi import FastAPI
from app.routes import dashboard_router

app = FastAPI(title="Admin Dashboard Service")

app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])