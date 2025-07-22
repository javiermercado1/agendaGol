from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import dashboard_router

app = FastAPI(title="Admin Dashboard Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "admin_dashboard"}