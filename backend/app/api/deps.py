from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings

security = HTTPBearer()

async def check_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verifica API key nell'header Authorization"""
    if credentials.credentials != settings.dev_api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return credentials.credentials

def get_current_settings():
    """Restituisce le impostazioni correnti"""
    return settings