from jwt import encode
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from .config import settings

import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")


def create_token(data: dict, expires_in_minutes: int = settings.access_token_expire_minutes) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expires_in_minutes)
    # Add unique ID (jti) for blacklisting and refresh token support
    to_encode.update({
        "exp": expire,
        "iat": now,
        "nbf": now,
        "jti": str(uuid.uuid4())
    })
    return encode(payload=to_encode, key=settings.secret_key, algorithm=settings.algorithm)


def create_refresh_token(data: dict) -> str:
    return create_token(data, expires_in_minutes=settings.refresh_token_expire_days * 24 * 60)