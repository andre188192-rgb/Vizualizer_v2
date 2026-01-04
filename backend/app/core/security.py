import secrets

from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .settings import settings

security = HTTPBasic()


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


def get_current_user(credentials: HTTPBasicCredentials = Depends(security)) -> str:
    is_user = secrets.compare_digest(credentials.username, settings.basic_user)
    is_pass = secrets.compare_digest(credentials.password, settings.basic_pass)
    if not (is_user and is_pass):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return credentials.username
