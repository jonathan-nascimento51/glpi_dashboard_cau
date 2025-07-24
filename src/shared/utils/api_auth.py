import os

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

API_TOKEN = os.getenv("DASHBOARD_API_TOKEN")
api_key_header = APIKeyHeader(name="X-API-Token", auto_error=False)


def verify_api_key(api_key: str = Security(api_key_header)) -> bool:
    """Verify dashboard API token."""
    if API_TOKEN and api_key == API_TOKEN:
        return True
    if API_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True
