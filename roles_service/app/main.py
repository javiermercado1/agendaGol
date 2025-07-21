from fastapi import FastAPI
from app.routes import roles_router

app = FastAPI(title="Roles and Permissions Service")

app.include_router(roles_router, prefix="/roles", tags=["Roles"])