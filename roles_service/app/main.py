from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import roles_router
from app.database import init_db

app = FastAPI(title="Roles and Permissions Service")

init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

app.include_router(roles_router, prefix="/roles", tags=["Roles"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "roles_service"}