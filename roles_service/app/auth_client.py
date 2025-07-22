import os
import requests
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL")

def validate_user_token(token: str):

    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{AUTH_SERVICE_URL}/auth/me", headers=headers, timeout=5)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=401, detail="Invalid token")
            
    except requests.RequestException:
        raise HTTPException(status_code=503, detail="Auth service unavailable")

def validate_admin_token(token: str):
    user_data = validate_user_token(token)
    
    if not user_data.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    
    return user_data

def get_user_id_from_token(token: str) -> int:
    user_data = validate_user_token(token)
    return user_data.get("id")
