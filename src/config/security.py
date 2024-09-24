from dotenv import load_dotenv
from datetime import (
    datetime, 
    timedelta, 
    timezone,
)
from typing import Any
from jwt import (
    encode, 
    decode,
)
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM="HS256"

def create_token(data: dict):    
    token: str = encode(payload=data, key=SECRET_KEY, algorithm=ALGORITHM) 
    return token

def validate_token(token: str) -> dict:
    data : dict =decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
    return data