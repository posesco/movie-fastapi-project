from dotenv import load_dotenv
from jwt import (
    encode, 
    decode,
)
import os

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

def create_token(data: dict):
    token: str = encode(payload=data, key=SECRET_KEY, algorithm="HS256") 
    return token

def validate_token(token: str) -> dict:
    data : dict =decode(token, key=SECRET_KEY, algorithms=['HS256'])
    return data