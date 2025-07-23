#!/usr/bin/env python3

import asyncio
import httpx
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8080/api/v1"

class GatewayTester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.token = None
    
    async def test_health_checks(self):
        """Probar health checks"""
        print("🔍 Testing health checks...")
        
        # Test gateway health
        try:
            response = await self.client.get("http://localhost:8080/health")
            print(f"✅ Gateway health: {response.status_code}")
        except Exception as e:
            print(f"❌ Gateway health failed: {e}")
        
        # Test services status
        try:
            response = await self.client.get("http://localhost:8080/services/status")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Services status: {len(data.get('services', {}))} services")
                for service, status in data.get('services', {}).items():
                    icon = "✅" if status.get('status') == 'healthy' else "❌"
                    print(f"  {icon} {service}: {status.get('status', 'unknown')}")
            else:
                print(f"❌ Services status failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Services status failed: {e}")
    
    async def test_auth_endpoints(self):
        """Probar endpoints de autenticación"""
        print("\n🔐 Testing auth endpoints...")
        
        # Test register
        user_data = {
            "username": f"testuser_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
        
        try:
            response = await self.client.post(f"{BASE_URL}/auth/register", json=user_data)
            if response.status_code in [200, 201]:
                print("✅ User registration successful")
                # Test login
                login_data = {
                    "username": user_data["username"],
                    "password": user_data["password"]
                }
                login_response = await self.client.post(f"{BASE_URL}/auth/login", json=login_data)
                if login_response.status_code == 200:
                    self.token = login_response.json().get("access_token")
                    print("✅ User login successful")
                else:
                    print(f"❌ Login failed: {login_response.status_code}")
            else:
                print(f"❌ Registration failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ Auth test failed: {e}")
    
    async def test_fields_endpoints(self):
        """Probar endpoints de canchas"""
        print("\n🏟️ Testing fields endpoints...")
        
        # Test list fields (público)
        try:
            response = await self.client.get(f"{BASE_URL}/fields/")
            print(f"✅ List fields: {response.status_code}")
        except Exception as e:
            print(f"❌ List fields failed: {e}")
        
        # Test create field (requiere admin)
        if self.token:
            field_data = {
                "name": f"Test Field {int(time.time())}",
                "location": "Test Location",
                "capacity": 10,
                "price_per_hour": 25.50,
                "opening_time": "09:00",
                "closing_time": "18:00",
                "is_active": True
            }
            
            try:
                headers = {"Authorization": f"Bearer {self.token}"}
                response = await self.client.post(f"{BASE_URL}/fields/", json=field_data, headers=headers)
                if response.status_code in [200, 201]:
                    print("✅ Create field successful")
                else:
                    print(f"⚠️ Create field failed (expected for non-admin): {response.status_code}")
            except Exception as e:
                print(f"❌ Create field failed: {e}")
    
    async def test_roles_endpoints(self):
        """Probar endpoints de roles"""
        print("\n👥 Testing roles endpoints...")
        
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            try:
                response = await self.client.get(f"{BASE_URL}/roles/roles", headers=headers)
                print(f"✅ List roles: {response.status_code}")
            except Exception as e:
                print(f"❌ List roles failed: {e}")
            
            try:
                response = await self.client.get(f"{BASE_URL}/roles/permissions", headers=headers)
                print(f"✅ List permissions: {response.status_code}")
            except Exception as e:
                print(f"❌ List permissions failed: {e}")
    
    async def test_reservations_endpoints(self):
        """Probar endpoints de reservas"""
        print("\n📅 Testing reservations endpoints...")
        
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            try:
                response = await self.client.get(f"{BASE_URL}/reservations/my", headers=headers)
                print(f"✅ Get my reservations: {response.status_code}")
            except Exception as e:
                print(f"❌ Get my reservations failed: {e}")
            
            try:
                response = await self.client.get(f"{BASE_URL}/reservations/", headers=headers)
                print(f"✅ List reservations: {response.status_code}")
            except Exception as e:
                print(f"❌ List reservations failed: {e}")
    
    async def test_dashboard_endpoints(self):
        """Probar endpoints del dashboard"""
        print("\n📊 Testing dashboard endpoints...")
        
        if self.token:
            headers = {"Authorization": f"Bearer {self.token}"}
            
            try:
                response = await self.client.get(f"{BASE_URL}/dashboard/health-check", headers=headers)
                print(f"✅ Dashboard health check: {response.status_code}")
            except Exception as e:
                print(f"❌ Dashboard health check failed: {e}")
    
    async def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 Starting API Gateway tests...\n")
        
        await self.test_health_checks()
        await self.test_auth_endpoints()
        await self.test_fields_endpoints()
        await self.test_roles_endpoints()
        await self.test_reservations_endpoints()
        await self.test_dashboard_endpoints()
        
        print("\n✨ Tests completed!")
    
    async def cleanup(self):
        """Limpieza"""
        await self.client.aclose()

async def main():
    tester = GatewayTester()
    try:
        await tester.run_all_tests()
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
