from fastapi import APIRouter
from fastapi.responses import JSONResponse
from jwt_manager import create_token
import os
from dotenv import load_dotenv
from schemas.user import User

load_dotenv()
ADMIN_USER= os.getenv("ADMIN_USER")
ADMIN_EMAIL= os.getenv("ADMIN_EMAIL")
ADMIN_PASS = os.getenv("ADMIN_PASS")

user_router = APIRouter()
   
@user_router.post('/login', tags=['Authentication'])
def login(user: User):
    if user.password == ADMIN_PASS and (user.email == ADMIN_EMAIL or user.username == ADMIN_USER):
        token: str = create_token(user.model_dump())
        return JSONResponse(status_code=200, content=token)
    else:
        return JSONResponse(status_code=404, content={"message" : "Usuario o contraseña no encontrada"})
        
    