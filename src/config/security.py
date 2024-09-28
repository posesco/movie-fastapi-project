from dotenv import load_dotenv
from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
import os
from datetime import datetime, timedelta, timezone


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")

if not SECRET_KEY:
    raise ValueError("El SECRET_KEY no está definido")

if not ALGORITHM:
    raise ValueError("El ALGORITHM no está definido")

if not ACCESS_TOKEN_EXPIRE_MINUTES:
    raise ValueError("El ACCESS_TOKEN_EXPIRE_MINUTES no está definido")
else:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(ACCESS_TOKEN_EXPIRE_MINUTES)


def create_token(data: dict, expires_in: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_in)
    to_encode.update({"exp": expire})
    token: str = encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return token


def validate_token(token: str) -> dict:
    try:
        data: dict = decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        return {"status": "success", "data": data}
    except ExpiredSignatureError as exec:
        return {"status": "token expired", "error": str(exec)}
    except InvalidTokenError as exec:
        return {"status": "invalid token", "error": str(exec)}
