from fastapi.security import HTTPBearer
from fastapi import Request, HTTPException
from jwt_manager import validate_token
import os
from dotenv import load_dotenv

load_dotenv()
ADMIN_PASS = os.getenv("ADMIN_PASS")

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        print(data)
        if data['password'] != ADMIN_PASS:
            raise HTTPException(status_code=403, detail="Credenciales invalidas")