import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from .config import get_settings

security = HTTPBasic(auto_error=False)


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    settings = get_settings()
    if settings.api_key and x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")


def get_current_user(credentials: HTTPBasicCredentials | None = Depends(security)) -> str:
    settings = get_settings()
    if not credentials:
        raise HTTPException(status_code=401, detail="Missing credentials")
    is_user = secrets.compare_digest(credentials.username, settings.basic_user)
    is_pass = secrets.compare_digest(credentials.password, settings.basic_pass)
    if not (is_user and is_pass):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return credentials.username


def create_access_token(subject: str, role: str) -> str:
    settings = get_settings()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_exp_minutes)
    payload = {"sub": subject, "role": role, "exp": expire}
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_client(
    authorization: str | None = Header(default=None),
    credentials: HTTPBasicCredentials | None = Depends(security),
) -> dict:
    settings = get_settings()
    if authorization and authorization.startswith("Bearer "):
        token = authorization.removeprefix("Bearer ").strip()
        try:
            payload = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        except jwt.PyJWTError as exc:
            raise HTTPException(status_code=401, detail="Invalid token") from exc
        return {"subject": payload.get("sub"), "role": payload.get("role")}

    user = get_current_user(credentials)
    return {"subject": user, "role": "ui"}


def require_roles(roles: set[str]):
    def dependency(client: dict = Depends(get_current_client)) -> dict:
        role = client.get("role")
        if role not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return client

    return dependency
