from fastapi import FastAPI
from app.routes import fields

app = FastAPI(title="Fields Management Service")

app.include_router(fields.router, prefix="/fields", tags=["Fields"])