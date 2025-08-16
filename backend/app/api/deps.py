from fastapi import HTTPException, Depends, Header
from typing import Optional
from app.core.config import settings

async def check_api_key(x_api_key: Optional[str] = Header(None)):
    """Verifica API key nell'header X-API-Key"""
    if not x_api_key or x_api_key != settings.dev_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key

def get_current_settings():
    """Restituisce le impostazioni correnti"""
    return settings