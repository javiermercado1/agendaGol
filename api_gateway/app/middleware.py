from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import time
import uuid

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de peticiones"""
    
    async def dispatch(self, request: Request, call_next):
        # Generar ID único para la petición
        request_id = str(uuid.uuid4())
        
        # Log de la petición entrante
        start_time = time.time()
        logger.info(
            f"Request {request_id}: {request.method} {request.url} "
            f"from {request.client.host if request.client else 'unknown'}"
        )
        
        # Ejecutar la petición
        response = await call_next(request)
        
        # Log de la respuesta
        process_time = time.time() - start_time
        logger.info(
            f"Response {request_id}: {response.status_code} "
            f"in {process_time:.3f}s"
        )
        
        # Agregar headers de respuesta
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = str(process_time)
        
        return response

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware para manejo de errores globales"""
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
            
            # Retornar respuesta de error genérica
            from fastapi.responses import JSONResponse
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred",
                    "type": "gateway_error"
                }
            )

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware para rate limiting (opcional)"""
    
    def __init__(self, app, calls: int = 100, period: int = 60):
        super().__init__(app)
        self.calls = calls
        self.period = period
        self.clients = {}
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host if request.client else "unknown"
        current_time = time.time()
        
        # Limpiar entradas antiguas
        self.clients = {
            ip: times for ip, times in self.clients.items()
            if any(t > current_time - self.period for t in times)
        }
        
        # Verificar rate limit
        if client_ip in self.clients:
            # Filtrar llamadas dentro del período
            recent_calls = [
                t for t in self.clients[client_ip] 
                if t > current_time - self.period
            ]
            
            if len(recent_calls) >= self.calls:
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Rate limit exceeded",
                        "message": f"Too many requests. Limit: {self.calls}/{self.period}s"
                    }
                )
            
            self.clients[client_ip] = recent_calls + [current_time]
        else:
            self.clients[client_ip] = [current_time]
        
        return await call_next(request)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware para agregar headers de seguridad"""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Agregar headers de seguridad
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response
