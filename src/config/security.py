from dotenv import load_dotenv
from jwt import encode, decode, ExpiredSignatureError
import os
from datetime import datetime, timedelta, timezone


load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"


def create_token(data: dict, expires_in: int = 15):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_in)
    to_encode.update({"exp": expire})
    token: str = encode(payload=to_encode, key=SECRET_KEY, algorithm=ALGORITHM)
    return token


def validate_token(token: str) -> dict:
    try:
        data: dict = decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        return data
    except ExpiredSignatureError:
        print("El Token ha expirado")
        return None
