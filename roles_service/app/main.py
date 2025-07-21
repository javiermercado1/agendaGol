from fastapi import FastAPI
from app.routes import roles

app = FastAPI(title="Roles and Permissions Service")

app.include_router(roles.router, prefix="/roles", tags=["Roles"])