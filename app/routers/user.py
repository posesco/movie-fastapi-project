from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from jwt_manager import create_token
import os
from dotenv import load_dotenv

load_dotenv()
ADMIN_EMAIL= os.getenv("ADMIN_EMAIL")
ADMIN_PASS = os.getenv("ADMIN_PASS")

user_router = APIRouter()

class User(BaseModel):
    email: EmailStr
    password: str = Field(min_length=5, max_length=100)
    
@user_router.post('/login', tags=['Authentication'])
def login(user: User):
    if user.email == ADMIN_EMAIL and user.password == ADMIN_PASS:
        token: str = create_token(user.model_dump())
        return JSONResponse(status_code=200, content=token)
    else:
        return JSONResponse(status_code=404, content={"message" : "Usuario no encontrado"})
        
    