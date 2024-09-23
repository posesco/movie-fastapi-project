from fastapi import APIRouter, Depends
from middlewares.jwt_bearer import JWTBearer
from fastapi.responses import JSONResponse
from jwt_manager import create_token
from fastapi.encoders import jsonable_encoder
import os
from dotenv import load_dotenv
from schemas.user import User
from services.user import UserService
from config.database import Session
from typing import List


load_dotenv()
ADMIN_USER= os.getenv("ADMIN_USER")
ADMIN_EMAIL= os.getenv("ADMIN_EMAIL")
ADMIN_PASS = os.getenv("ADMIN_PASS")

user_router = APIRouter()
   
@user_router.post('/login', tags=['users'])
def login(user: User):
    if user.password == ADMIN_PASS and (user.email == ADMIN_EMAIL or user.username == ADMIN_USER):
        token: str = create_token(user.model_dump())
        return JSONResponse(status_code=200, content=token)
    else:
        return JSONResponse(status_code=404, content={"message" : "Usuario o contraseña no encontrada"})
        
@user_router.post('/register', tags=['users'], response_model=dict, status_code=201, dependencies=[Depends(JWTBearer())])
def create_user(user: User) -> dict:
    db = Session()
    UserService(db).create_user(user)
    db.close()
    return JSONResponse(status_code=201, content={"message": "Usuario creado exitosamente"})

@user_router.delete('/users/{id}', tags=['users'], response_model=dict, status_code=200, dependencies=[Depends(JWTBearer())])
def delete_user(id: str ) -> dict:
    db = Session()
    result = UserService(db).delete_user(id)
    if result:
        db.close()
        return JSONResponse(status_code=200, content={"message" : "Usuario eliminado"})
    else:
        return JSONResponse(status_code=404, content={"message" : "Id de usuario no encontrado"})

@user_router.get('/users', tags=['users'], response_model=List[User], status_code=200, dependencies=[Depends(JWTBearer())])
def get_users() -> List[User]:
    db = Session()
    result= UserService(db).get_users()
    if result:
        return JSONResponse(status_code=200, content=jsonable_encoder(result))
    else:
        return JSONResponse(status_code=404, content={"message" : "No hay usuarios registrados"})

@user_router.get('/users/{username}', tags=['users'], response_model=List[User], status_code=200, dependencies=[Depends(JWTBearer())])
def get_user(username: str) -> List[User]:
    db = Session()
    result= UserService(db).get_user(username)
    db.close()
    if result:
        return JSONResponse(status_code=200, content=jsonable_encoder(result))
    else:
        return JSONResponse(status_code=404, content={"message" : f"Usuario {username} no encontrado"})