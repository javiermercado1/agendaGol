from fastapi import FastAPI
from app.routes import dashboard

app = FastAPI(title="Admin Dashboard Service")

app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])