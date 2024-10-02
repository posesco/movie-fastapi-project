from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import (
    HTTPException,
    APIRouter,
    Depends,
    Form,
)
from typing import Annotated, List
from sqlalchemy.orm import Session
from schemas.user import UserLogin, UserCreate
from middlewares.jwt_bearer import JWTBearer
from services.user import UserService
from config.db import get_db


user_router = APIRouter()


@user_router.post("/login/", tags=["users"])
def login(user: Annotated[UserLogin, Form()], db: Session = Depends(get_db)) -> dict:
    token = UserService(db).login_user(user)
    if token:
        return JSONResponse(status_code=200, content=token)
    else:
        raise HTTPException(
            status_code=404, detail={"error": "Usuario o contraseña no encontrada"}
        )


@user_router.post(
    "/users/register",
    tags=["users"],
    response_model=dict,
    status_code=201,
    dependencies=[Depends(JWTBearer())],
)
def create_user(
    user: Annotated[UserCreate, Form()], db: Session = Depends(get_db)
) -> dict:
    result = UserService(db).create_user(user)
    if result:
        return JSONResponse(
            status_code=201, content={"success": "Usuario creado exitosamente"}
        )
    else:
        raise HTTPException(status_code=409, detail={"error": "El usuario ya existe"})


# @user_router.post(
#     "/users/assign_role",
#     tags=["users"],
#     response_model=dict,
#     status_code=200,
#     dependencies=[Depends(JWTBearer())],
# )
# def assign_role(
#     username: str, roles: list, db: Session = Depends(get_db)
# ) -> dict:
#     existing_roles = UserService(db)._get_roles(roles)

#     if len(existing_roles) != len(roles):
#         raise HTTPException(
#             status_code=400,
#             detail={"error": "Uno o más roles especificados no existen"}
#         )

#     result = UserService(db).assign_roles(username, existing_roles)
#     if result:
#         return JSONResponse(
#             status_code=200,
#             content={"success": f"Roles: [{', '.join(r.name for r in existing_roles)}] asignados al usuario: {username}"},
#         )
#     else:
#         raise HTTPException(
#             status_code=404, detail={"error": "Error al asignar roles"}
#         )


@user_router.patch(
    "/users/new_pass",
    tags=["users"],
    response_model=dict,
    status_code=200,
    dependencies=[Depends(JWTBearer())],
)
def update_password(
    username: str, current_pass: str, new_pass: str, db: Session = Depends(get_db)
) -> dict:
    result = UserService(db).update_password(username, current_pass, new_pass)
    if result:
        return JSONResponse(
            status_code=200,
            content={"success": f"Contraseña actualizada para usuario: {username}"},
        )
    else:
        raise HTTPException(
            status_code=404, detail={"error": "Usuario o contraseña no encontrada"}
        )


@user_router.patch(
    "/users/change_state",
    tags=["users"],
    response_model=dict,
    status_code=200,
    dependencies=[Depends(JWTBearer())],
)
def change_state(username: str, state: bool, db: Session = Depends(get_db)) -> dict:
    result = UserService(db).state_user(username, state)
    if result:
        return JSONResponse(
            status_code=200,
            content={
                "success": f'El estado del usuario: {username} es {"habilitado" if state else "deshabilitado"}'
            },
        )
    else:
        raise HTTPException(status_code=404, detail={"error": "Usuario no encontrado"})


@user_router.delete(
    "/users/{username}",
    tags=["users"],
    response_model=dict,
    status_code=200,
    dependencies=[Depends(JWTBearer())],
)
def delete_user(username: str, db: Session = Depends(get_db)) -> dict:
    result = UserService(db).delete_user(username)
    if result:
        return JSONResponse(status_code=200, content={"success": "Usuario eliminado"})
    else:
        raise HTTPException(status_code=404, detail={"error": "Usuario no encontrado"})


@user_router.get(
    "/users",
    tags=["users"],
    response_model=List[UserCreate],
    status_code=200,
    dependencies=[Depends(JWTBearer())],
)
def get_users(db: Session = Depends(get_db)) -> List[UserCreate]:
    users_info = UserService(db).get_users()
    if users_info:
        return JSONResponse(status_code=200, content=jsonable_encoder(users_info))
    else:
        raise HTTPException(
            status_code=404, detail={"error": "No hay usuarios registrados"}
        )


@user_router.get(
    "/users/{username}",
    tags=["users"],
    response_model=List[UserCreate],
    status_code=200,
    dependencies=[Depends(JWTBearer())],
)
def get_user(username: str, db: Session = Depends(get_db)) -> list[UserCreate]:
    user_info = UserService(db).get_user(username)
    if user_info:
        return JSONResponse(status_code=200, content=jsonable_encoder(user_info))
    else:
        raise HTTPException(
            status_code=404, detail={"error": f"Usuario {username} no encontrado"}
        )
