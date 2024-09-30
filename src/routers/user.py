from fastapi import (
    APIRouter,
    Depends,
    Form,
)
from middlewares.jwt_bearer import JWTBearer
from fastapi.responses import JSONResponse
from services.user import UserService

from config.db import Session
from typing import Annotated, List
from fastapi.encoders import jsonable_encoder
from schemas.user import UserLogin, UserCreate


user_router = APIRouter()


@user_router.post("/login/", tags=["users"])
def login(user: Annotated[UserLogin, Form()]) -> dict:
    db = Session()
    token = UserService(db).login_user(user)
    db.close()
    if token:
        return JSONResponse(status_code=200, content=token)
    else:
        return JSONResponse(
            status_code=404, content={"error": "Usuario o contraseña no encontrada"}
        )


@user_router.post(
    "/users/register",
    tags=["users"],
    response_model=dict,
    status_code=201,
    dependencies=[Depends(JWTBearer())],
)
def create_user(user: Annotated[UserCreate, Form()]) -> dict:
    db = Session()
    result = UserService(db).create_user(user)
    db.close()
    if result:
        return JSONResponse(
            status_code=201, content={"success": "Usuario creado exitosamente"}
        )
    else:
        return JSONResponse(status_code=409, content={"error": "El usuario ya existe"})


@user_router.patch(
    "/users/new_pass",
    tags=["users"],
    response_model=dict,
    status_code=200,
    dependencies=[Depends(JWTBearer())],
)
def update_password(username: str, current_pass: str, new_pass: str) -> dict:
    db = Session()
    result = UserService(db).update_password(username, current_pass, new_pass)
    db.close()
    if result:
        return JSONResponse(
            status_code=200,
            content={"success": f"Contraseña actualizada para usuario: {username}"},
        )
    else:
        return JSONResponse(
            status_code=404, content={"error": "Usuario o contraseña no encontrada"}
        )


@user_router.delete(
    "/users/{username}",
    tags=["users"],
    response_model=dict,
    status_code=200,
    dependencies=[Depends(JWTBearer())],
)
def delete_user(username: str) -> dict:
    db = Session()
    result = UserService(db).delete_user(username)
    if result:
        db.close()
        return JSONResponse(status_code=200, content={"success": "Usuario eliminado"})
    else:
        return JSONResponse(
            status_code=404, content={"error": "Id de usuario no encontrado"}
        )


@user_router.get(
    "/users",
    tags=["users"],
    response_model=List[UserCreate],
    status_code=200,
    dependencies=[Depends(JWTBearer())],
)
def get_users() -> List[UserCreate]:
    db = Session()
    users_info = UserService(db).get_users()
    if users_info:
        return JSONResponse(status_code=200, content=jsonable_encoder(users_info))
    else:
        return JSONResponse(
            status_code=404, content={"error": "No hay usuarios registrados"}
        )


@user_router.get(
    "/users/{username}",
    tags=["users"],
    response_model=List[UserCreate],
    status_code=200,
    dependencies=[Depends(JWTBearer())],
)
def get_user(username: str) -> list[UserCreate]:
    db = Session()
    user_info = UserService(db).get_user(username)
    db.close()
    if user_info:
        return JSONResponse(status_code=200, content=jsonable_encoder(user_info))
    else:
        return JSONResponse(
            status_code=404, content={"error": f"Usuario {username} no encontrado"}
        )
