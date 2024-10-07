from jwt import encode
from datetime import datetime, timedelta, timezone
from config.settings import settings
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = int(settings.access_token_expire_minutes)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def create_token(data: dict, expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expires_in)
    to_encode.update({"exp": expire, "iat": now, "nbf": now})
    token: str = encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return token
