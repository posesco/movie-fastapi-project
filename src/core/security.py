from jwt import encode
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/user/login")


def create_token(data: dict, expires_in: int = settings.access_token_expire_minutes) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expires_in)
    to_encode.update({"exp": expire, "iat": now, "nbf": now})
    return encode(payload=to_encode, key=settings.secret_key, algorithm=settings.algorithm)