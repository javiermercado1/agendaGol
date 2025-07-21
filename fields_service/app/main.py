from fastapi import FastAPI
from app.routes import fields_router

app = FastAPI(title="Fields Management Service")

app.include_router(fields_router, prefix="/fields", tags=["Fields"])