import os
from typing import Dict, Any, List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Configuración del API Gateway"""
    
    # API Gateway
    gateway_host: str = "0.0.0.0"
    gateway_port: int = 8080
    gateway_workers: int = 1
    
    # Services
    auth_service_url: str = "http://auth_service:8000"
    roles_service_url: str = "http://roles_service:8001"
    fields_service_url: str = "http://fields_service:8002"
    reservations_service_url: str = "http://reservations_service:8003"
    admin_dashboard_url: str = "http://admin_dashboard:8004"
    
    # Logging
    log_level: str = "INFO"
    
    # Security
    rate_limit_calls: int = 100
    rate_limit_period: int = 60
    
    # CORS
    cors_origins: List[str] = ["*"]
    cors_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    cors_headers: List[str] = ["*"]
    
    # Timeouts
    service_timeout: int = 30
    health_check_timeout: int = 5
    
    # Circuit breaker
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_timeout: int = 60
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Instancia global de configuración
settings = Settings()

# Configuración de servicios
SERVICES_CONFIG = {
    "auth_service": {
        "url": settings.auth_service_url,
        "prefix": "/auth",
        "timeout": settings.service_timeout,
        "health_endpoint": "/health"
    },
    "roles_service": {
        "url": settings.roles_service_url,
        "prefix": "/roles", 
        "timeout": settings.service_timeout,
        "health_endpoint": "/health"
    },
    "fields_service": {
        "url": settings.fields_service_url,
        "prefix": "/fields",
        "timeout": settings.service_timeout,
        "health_endpoint": "/health"
    },
    "reservations_service": {
        "url": settings.reservations_service_url,
        "prefix": "/reservations",
        "timeout": settings.service_timeout,
        "health_endpoint": "/health"
    },
    "admin_dashboard": {
        "url": settings.admin_dashboard_url,
        "prefix": "/dashboard",
        "timeout": settings.service_timeout,
        "health_endpoint": "/health"
    }
}
