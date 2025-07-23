from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
import httpx
import os
import logging
from typing import Dict, Any, Optional
import asyncio

from app.config import SERVICES_CONFIG

logger = logging.getLogger(__name__)

class APIGateway:
    def __init__(self):
        self.config = SERVICES_CONFIG
        self.router = APIRouter()
        self.client = httpx.AsyncClient(timeout=30.0)
        self._setup_routes()

    def _setup_routes(self):
        """Configurar todas las rutas del gateway"""
        
        # Auth Service Routes
        self._add_auth_routes()
        
        # Roles Service Routes  
        self._add_roles_routes()
        
        # Fields Service Routes
        self._add_fields_routes()
        
        # Reservations Service Routes
        self._add_reservations_routes()
        
        # Dashboard Routes
        self._add_dashboard_routes()

    def _add_auth_routes(self):
        """Rutas del servicio de autenticación"""
        
        @self.router.post("/auth/register")
        async def register(request: Request):
            return await self._proxy_request("auth_service", "/auth/register", request)
        
        @self.router.post("/auth/login")
        async def login(request: Request):
            return await self._proxy_request("auth_service", "/auth/login", request)
        
        @self.router.get("/auth/verify")
        async def verify_token(request: Request):
            return await self._proxy_request("auth_service", "/auth/verify", request)
        
        @self.router.post("/auth/password-recovery")
        async def password_recovery(request: Request):
            return await self._proxy_request("auth_service", "/auth/password-recovery", request)
        
        @self.router.patch("/auth/profile")
        async def update_profile(request: Request):
            return await self._proxy_request("auth_service", "/auth/profile", request)
        
        @self.router.get("/auth/me")
        async def get_current_user(request: Request):
            return await self._proxy_request("auth_service", "/auth/me", request)
        
        @self.router.post("/auth/register-admin")
        async def register_admin(request: Request):
            return await self._proxy_request("auth_service", "/auth/register-admin", request)
        
        @self.router.get("/auth/users")
        async def get_users(request: Request):
            return await self._proxy_request("auth_service", "/auth/users", request)
        
        @self.router.get("/auth/users/stats")
        async def get_users_stats(request: Request):
            return await self._proxy_request("auth_service", "/auth/users/stats", request)
        
        @self.router.get("/auth/user/{user_id}")
        async def get_user_by_id(user_id: int, request: Request):
            return await self._proxy_request("auth_service", f"/auth/user/{user_id}", request)

    def _add_roles_routes(self):
        """Rutas del servicio de roles"""
        
        @self.router.post("/roles/validate-permission")
        async def validate_permission(request: Request):
            return await self._proxy_request("roles_service", "/roles/validate-permission", request)
        
        @self.router.get("/roles/roles")
        async def get_roles(request: Request):
            return await self._proxy_request("roles_service", "/roles/roles", request)
        
        @self.router.post("/roles/roles")
        async def create_role(request: Request):
            return await self._proxy_request("roles_service", "/roles/roles", request)
        
        @self.router.get("/roles/permissions")
        async def get_permissions(request: Request):
            return await self._proxy_request("roles_service", "/roles/permissions", request)
        
        @self.router.post("/roles/permissions")
        async def create_permission(request: Request):
            return await self._proxy_request("roles_service", "/roles/permissions", request)
        
        @self.router.post("/roles/users/{user_id}/assign-role")
        async def assign_role(user_id: int, request: Request):
            return await self._proxy_request("roles_service", f"/roles/users/{user_id}/assign-role", request)
        
        @self.router.get("/roles/users/{user_id}/permissions")
        async def get_user_permissions(user_id: int, request: Request):
            return await self._proxy_request("roles_service", f"/roles/users/{user_id}/permissions", request)
        
        @self.router.post("/roles/roles/{role_id}/permissions")
        async def assign_permission_to_role(role_id: int, request: Request):
            return await self._proxy_request("roles_service", f"/roles/roles/{role_id}/permissions", request)

    def _add_fields_routes(self):
        """Rutas del servicio de canchas"""
        
        @self.router.post("/fields/")
        async def create_field(request: Request):
            return await self._proxy_request("fields_service", "/fields/", request)
        
        @self.router.get("/fields/")
        async def list_fields(request: Request):
            return await self._proxy_request("fields_service", "/fields/", request)
        
        @self.router.get("/fields/{field_id}")
        async def get_field(field_id: int, request: Request):
            return await self._proxy_request("fields_service", f"/fields/{field_id}", request)
        
        @self.router.put("/fields/{field_id}")
        async def update_field(field_id: int, request: Request):
            return await self._proxy_request("fields_service", f"/fields/{field_id}", request)
        
        @self.router.delete("/fields/{field_id}")
        async def delete_field(field_id: int, request: Request):
            return await self._proxy_request("fields_service", f"/fields/{field_id}", request)
        
        @self.router.get("/fields/{field_id}/availability")
        async def get_field_availability(field_id: int, request: Request):
            return await self._proxy_request("fields_service", f"/fields/{field_id}/availability", request)

    def _add_reservations_routes(self):
        """Rutas del servicio de reservas"""
        
        @self.router.post("/reservations/")
        async def create_reservation(request: Request):
            return await self._proxy_request("reservations_service", "/reservations/", request)
        
        @self.router.get("/reservations/")
        async def list_reservations(request: Request):
            return await self._proxy_request("reservations_service", "/reservations/", request)
        
        @self.router.get("/reservations/my")
        async def get_my_reservations(request: Request):
            return await self._proxy_request("reservations_service", "/reservations/my", request)
        
        @self.router.get("/reservations/{reservation_id}")
        async def get_reservation(reservation_id: int, request: Request):
            return await self._proxy_request("reservations_service", f"/reservations/{reservation_id}", request)
        
        @self.router.put("/reservations/{reservation_id}")
        async def update_reservation(reservation_id: int, request: Request):
            return await self._proxy_request("reservations_service", f"/reservations/{reservation_id}", request)
        
        @self.router.post("/reservations/{reservation_id}/cancel")
        async def cancel_reservation(reservation_id: int, request: Request):
            return await self._proxy_request("reservations_service", f"/reservations/{reservation_id}/cancel", request)
        
        @self.router.get("/reservations/field/{field_id}/date/{date}")
        async def get_reservations_by_field_date(field_id: int, date: str, request: Request):
            return await self._proxy_request("reservations_service", f"/reservations/field/{field_id}/date/{date}", request)
        
        @self.router.get("/reservations/stats/")
        async def get_reservations_stats(request: Request):
            return await self._proxy_request("reservations_service", "/reservations/stats/", request)

    def _add_dashboard_routes(self):
        """Rutas del dashboard administrativo"""
        
        @self.router.get("/dashboard/stats")
        async def get_dashboard_stats(request: Request):
            return await self._proxy_request("admin_dashboard", "/dashboard/stats", request)
        
        @self.router.get("/dashboard/users")
        async def get_dashboard_users(request: Request):
            return await self._proxy_request("admin_dashboard", "/dashboard/users", request)
        
        @self.router.get("/dashboard/reservations")
        async def get_dashboard_reservations(request: Request):
            return await self._proxy_request("admin_dashboard", "/dashboard/reservations", request)
        
        @self.router.get("/dashboard/fields/stats")
        async def get_dashboard_fields_stats(request: Request):
            return await self._proxy_request("admin_dashboard", "/dashboard/fields/stats", request)
        
        @self.router.get("/dashboard/revenue/daily")
        async def get_dashboard_revenue(request: Request):
            return await self._proxy_request("admin_dashboard", "/dashboard/revenue/daily", request)
        
        @self.router.get("/dashboard/health-check")
        async def get_dashboard_health(request: Request):
            return await self._proxy_request("admin_dashboard", "/dashboard/health-check", request)

    async def _proxy_request(self, service_name: str, path: str, request: Request):
        """Proxy de peticiones a los microservicios"""
        try:
            service_config = self.config.get(service_name)
            if not service_config:
                raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
            
            # Construir URL del servicio
            service_url = f"{service_config['url']}{path}"
            
            # Obtener query parameters
            query_params = dict(request.query_params)
            
            # Obtener headers (filtrar algunos headers internos)
            headers = dict(request.headers)
            headers_to_remove = ['host', 'content-length']
            for header in headers_to_remove:
                headers.pop(header, None)
            
            # Obtener el body si existe
            body = None
            if request.method in ['POST', 'PUT', 'PATCH']:
                body = await request.body()
            
            logger.info(f"Proxying {request.method} {service_url}")
            
            # Realizar la petición al microservicio
            response = await self.client.request(
                method=request.method,
                url=service_url,
                params=query_params,
                headers=headers,
                content=body,
                timeout=service_config['timeout']
            )
            
            # Retornar la respuesta
            return JSONResponse(
                content=response.json() if response.content else {},
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
        except httpx.TimeoutException:
            logger.error(f"Timeout connecting to {service_name}")
            raise HTTPException(status_code=504, detail=f"Service {service_name} timeout")
        except httpx.ConnectError:
            logger.error(f"Connection error to {service_name}")
            raise HTTPException(status_code=503, detail=f"Service {service_name} unavailable")
        except Exception as e:
            logger.error(f"Error proxying request to {service_name}: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal gateway error")

    async def check_services_health(self) -> Dict[str, Any]:
        """Verificar la salud de todos los servicios"""
        health_status = {}
        
        async def check_service(service_name: str, config: Dict[str, Any]):
            try:
                response = await self.client.get(
                    f"{config['url']}/health",
                    timeout=5.0
                )
                health_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "response_time": response.elapsed.total_seconds(),
                    "status_code": response.status_code
                }
            except Exception as e:
                health_status[service_name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        # Verificar todos los servicios en paralelo
        tasks = [
            check_service(name, config) 
            for name, config in self.config.items()
        ]
        await asyncio.gather(*tasks, return_exceptions=True)
        
        return {
            "gateway_status": "healthy",
            "services": health_status,
            "timestamp": str(asyncio.get_event_loop().time())
        }

    async def cleanup(self):
        """Limpieza al cerrar el gateway"""
        await self.client.aclose()
