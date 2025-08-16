from fastapi import Header, HTTPException, status
from app.core.config import get_settings

async def check_api_key(x_api_key: str = Header(None)):
    if x_api_key != get_settings().DEV_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
