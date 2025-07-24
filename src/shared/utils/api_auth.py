import os

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Token", auto_error=False)


def verify_api_key(api_key: str | None = Security(api_key_header)) -> bool:
    """Verify dashboard API token."""
    token = os.getenv("DASHBOARD_API_TOKEN")
    if token and api_key == token:
        return True
    if token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True
