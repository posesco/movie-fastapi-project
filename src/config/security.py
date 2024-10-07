from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta, timezone
from config.settings import settings

ACCESS_TOKEN_EXPIRE_MINUTES = int(settings.access_token_expire_minutes)


def create_token(data: dict, expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=expires_in)
    to_encode.update({"exp": expire, "iat": now, "nbf": now})
    token: str = encode(
        payload=to_encode, key=settings.secret_key, algorithm=settings.algorithm
    )
    return token


def validate_token(token: str) -> dict:
    try:
        data: dict = decode(
            token, key=settings.secret_key, algorithms=[settings.algorithm]
        )
        return {"status": "success", "data": data}
    except ExpiredSignatureError as exec:
        return {"status": "token expired", "error": str(exec)}
    except InvalidTokenError as exec:
        return {"status": "invalid token", "error": str(exec)}
