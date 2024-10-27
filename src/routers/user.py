from fastapi import HTTPException, APIRouter, Depends, Form, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from typing import Annotated, Optional
from src.schemas.user import UserCreate
from src.schemas.token import Token
from src.services.user import UserService
from src.config.db import get_db
from src.config.settings import settings
from src.config.security import pwd_context
from src.models.user import User as UserModel


ADMIN_PASS_HASHED = pwd_context.hash(settings.admin_pass)

user_router = APIRouter()


@user_router.post("/login", tags=["Users"], response_model=Token)
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Optional[Token]:
    check_username = UserService(db).get_username(form_data.username)
    if not check_username:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "El usuario no existe"},
            headers={"WWW-Authenticate": "Bearer"},
        )

    password_valid = UserService(db).verify_password(
        form_data.password, check_username.password
    )
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "Password incorrecto"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_info = {
        "id": str(check_username.id),
        "roles": [str(role.id) for role in check_username.roles],
        "client_ip": request.client.host,
        "url": str(request.url),
    }
    data = {
        "sub": form_data.username,
        "user_info": user_info,
    }
    token = UserService(db).get_token(data)
    return Token(access_token=token, token_type="bearer")


@user_router.post(
    "/users/register",
    tags=["Users"],
    status_code=201,
    response_model=UserCreate,
)
async def create_user(
    user: Annotated[UserCreate, Form()],
    current_user: Annotated[UserModel, Depends(UserService.get_current_active_user)],
    db: Session = Depends(get_db),
) -> Optional[UserCreate]:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "No autenticado"},
        )

    check_username = UserService(db).get_username(user.username)
    check_email = UserService(db).get_email(user.email)

    if check_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "El nombre de usuario ya existe"},
        )
    if check_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "El correo electrónico ya existe"},
        )

    new_user = UserService(db).create_user(user)
    if new_user:
        return JSONResponse(
            status_code=201, content={"success": "Usuario creado exitosamente"}
        )
    else:
        raise HTTPException(
            status_code=500, detail={"error": "No se pudo crear usuario"}
        )


# @user_router.post(
#     "/users/assign_role",
#     tags=["Users"],
#     response_model=dict,
#     status_code=status.HTTP_200_OK,
#     dependencies=[Depends(JWTBearer())],
# )
# def assign_role(
#     username: str, roles: list, db: Session = Depends(get_db)
# ) -> dict:
#
#     existing_roles = UserService(db)._get_roles(roles)

#     if len(existing_roles) != len(roles):
#         raise HTTPException(
#             status_code=400,
#             detail={"error": "Uno o más roles especificados no existen"}
#         )

#     result = UserService(db).assign_roles(username, existing_roles)
#     if result:
#         return JSONResponse(
#             status_code=status.HTTP_200_OK,
#             content={"success": f"Roles: [{', '.join(r.name for r in existing_roles)}] asignados al usuario: {username}"},
#         )
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail={"error": "Error al asignar roles"}
#         )


# @user_router.patch(
#     "/users/new_pass",
#     tags=["Users"],
#     response_model=dict,
#     status_code=status.HTTP_200_OK,
#     dependencies=[Depends(JWTBearer())],
# )
# def update_password(
#     username: str, current_pass: str, new_pass: str, db: Session = Depends(get_db)
# ) -> dict:
#
#     check_username = UserService(db).get_username(username)
#     if not check_username:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail={"error": "Usuario no existe"}
#         )
#     check_currentpass = UserService(db).verify_password(
#         current_pass, check_username.password
#     )
#     if not check_currentpass:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail={"error": "La contraseña actual no coincide"},
#         )
#     result = UserService(db).update_password(username, new_pass)
#     if result:
#         return JSONResponse(
#             status_code=status.HTTP_200_OK,
#             content={"success": f"Contraseña actualizada para usuario: {username}"},
#         )


# @user_router.patch(
#     "/users/change_state",
#     tags=["Users"],
#     response_model=dict,
#     status_code=status.HTTP_200_OK,
#     dependencies=[Depends(JWTBearer())],
# )
# def change_state(username: str, state: bool, db: Session = Depends(get_db)) -> dict:
#     check_username = UserService(db).get_username(username)
#     if not check_username:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail={"error": "El usuario no existe"},
#         )
#     if check_username.is_active == state:
#         raise HTTPException(
#             status_code=status.HTTP_409_CONFLICT,
#             detail={
#                 "error": f'El estado actual es {"habilitado" if state else "deshabilitado"}'
#             },
#         )
#     result = UserService(db).state_user(check_username, state)
#     if result:
#         return JSONResponse(
#             status_code=status.HTTP_200_OK,
#             content={
#                 "success": f'El estado del usuario: {username} es {"habilitado" if state else "deshabilitado"}'
#             },
#         )


# @user_router.delete(
#     "/users/{username}",
#     tags=["Users"],
#     response_model=dict,
#     status_code=status.HTTP_200_OK,
#     dependencies=[Depends(JWTBearer())],
# )
# def delete_user(username: str, db: Session = Depends(get_db)) -> dict:
#     check_username = UserService(db).get_username(username)
#     if not check_username:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail={"error": "El usuario no existe"},
#         )
#     result = UserService(db).delete_user(username)
#     if result:
#         return JSONResponse(
#             status_code=status.HTTP_200_OK, content={"success": "Usuario eliminado"}
#         )
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail={"error": "Usuario no encontrado"},
#         )


# @user_router.get(
#     "/users",
#     tags=["Users"],
#     response_model=List[UserCreate],
#     status_code=status.HTTP_200_OK,
#     dependencies=[Depends(JWTBearer())],
# )
# def get_users(db: Session = Depends(get_db)) -> List[UserCreate]:
#     users_info = UserService(db).get_users()
#     if users_info:
#         return JSONResponse(
#             status_code=status.HTTP_200_OK, content=jsonable_encoder(users_info)
#         )
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail={"error": "No hay usuarios registrados"},
#         )


# @user_router.get(
#     "/users/{username}",
#     tags=["Users"],
#     response_model=List[UserCreate],
#     status_code=status.HTTP_200_OK,
#     dependencies=[Depends(JWTBearer())],
# )
# def get_user(username: str, db: Session = Depends(get_db)) -> list[UserCreate]:
#     user_info = UserService(db).get_username(username)
#     if user_info:
#         return JSONResponse(
#             status_code=status.HTTP_200_OK, content=jsonable_encoder(user_info)
#         )
#     else:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail={"error": f"Usuario {username} no encontrado"},
#         )
