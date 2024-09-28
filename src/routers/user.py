from fastapi.encoders import jsonable_encoder
from fastapi import (
    APIRouter,
    Depends,
    Form,
)
from middlewares.jwt_bearer import JWTBearer
from fastapi.responses import JSONResponse
from services.user import UserService

from config.db import Session
from typing import (
    List,
    Annotated,
)

from schemas.user import User, UserCreate


user_router = APIRouter()


@user_router.post("/login/", tags=["users"])
def login(user: Annotated[User, Form()]):
    db = Session()
    token = UserService(db).login_user(user)
    db.close()
    if token:
        return JSONResponse(status_code=200, content=token)
    else:
        return JSONResponse(
            status_code=404, content={"message": "Usuario o contraseña no encontrada"}
        )


@user_router.post(
    "/register",
    tags=["users"],
    response_model=dict,
    status_code=201,
    dependencies=[Depends(JWTBearer())],
)
def create_user(user: UserCreate) -> dict:
    db = Session()
    UserService(db).create_user(user)
    db.close()
    return JSONResponse(
        status_code=201, content={"message": "Usuario creado exitosamente"}
    )


@user_router.patch(
    "/users/pass",
    tags=["users"],
    response_model=dict,
    status_code=200,
    dependencies=[Depends(JWTBearer())],
)
def update_password(username: str, current_pass: str, new_pass: str) -> dict:
    pass
    # db = Sesszion()
    # UserService(db).update_password(id, new_pass)
    # db.close()
    # return JSONResponse(
    #     status_code=200, content={"message": "Usuario creado exitosamente"}
    # )


@user_router.delete(
    "/users/{id}",
    tags=["users"],
    response_model=dict,
    status_code=200,
    dependencies=[Depends(JWTBearer())],
)
def delete_user(id: str) -> dict:
    db = Session()
    result = UserService(db).delete_user(id)
    if result:
        db.close()
        return JSONResponse(status_code=200, content={"message": "Usuario eliminado"})
    else:
        return JSONResponse(
            status_code=404, content={"message": "Id de usuario no encontrado"}
        )


@user_router.get(
    "/users",
    tags=["users"],
    response_model=List[User],
    status_code=200,
    dependencies=[Depends(JWTBearer())],
)
def get_users() -> List[User]:
    db = Session()
    result = UserService(db).get_users()
    if result:
        return JSONResponse(status_code=200, content=jsonable_encoder(result))
    else:
        return JSONResponse(
            status_code=404, content={"message": "No hay usuarios registrados"}
        )


@user_router.get(
    "/users/{username}",
    tags=["users"],
    response_model=List[User],
    status_code=200,
    dependencies=[Depends(JWTBearer())],
)
def get_user(username: str) -> List[User]:
    db = Session()
    result = UserService(db).get_user(username)
    db.close()
    if result:
        return JSONResponse(status_code=200, content=jsonable_encoder(result))
    else:
        return JSONResponse(
            status_code=404, content={"message": f"Usuario {username} no encontrado"}
        )
