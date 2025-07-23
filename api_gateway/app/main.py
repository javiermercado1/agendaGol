from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import os

from app.gateway import APIGateway
from app.middleware import RequestLoggingMiddleware, ErrorHandlingMiddleware
from app.config import settings

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sport Fields API Gateway",
    description="API Gateway para el sistema de gestión de canchas deportivas",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Middleware personalizado
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)

# Inicializar el gateway
gateway = APIGateway()

# Incluir todas las rutas del gateway
app.include_router(gateway.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Sport Fields API Gateway",
        "version": "1.0.0",
        "services": [
            "auth_service",
            "roles_service", 
            "fields_service",
            "reservations_service",
            "admin_dashboard"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "api_gateway",
        "version": "1.0.0"
    }

@app.get("/services/status")
async def services_status():
    """Check status of all microservices"""
    return await gateway.check_services_health()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
