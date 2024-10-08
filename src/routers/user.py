from fastapi import HTTPException, APIRouter, Depends, Form, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Annotated, Optional
from schemas.user import UserCreate
from schemas.token import Token
from services.user import UserService
from config.db import get_db
from config.settings import settings
from config.security import pwd_context
from fastapi.security import OAuth2PasswordRequestForm


ADMIN_PASS_HASHED = pwd_context.hash(settings.admin_pass)

user_router = APIRouter()


@user_router.post("/login", tags=["Users"], response_model=Token)
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> Optional[Token]:
    user_service = UserService(db)

    if form_data.username == settings.admin_user:
        password_valid = user_service.verify_password(
            form_data.username, ADMIN_PASS_HASHED
        )
    else:
        check_username = user_service.get_username(form_data.username)
        if not check_username:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={"error": "El usuario no existe"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        password_valid = user_service.verify_password(
            form_data.username, check_username.password
        )

    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "Password incorrecto"},
            headers={"WWW-Authenticate": "Bearer"},
        )
    request_data = {
        "headers": dict(request.headers),
        "client_ip": request.client.host,
        "method": request.method,
        "url": str(request.url),
        "path_params": request.path_params,
        "query_params": dict(request.query_params),
        "cookies": request.cookies,
    }
    data = {
        "sub": form_data.username,
        "user_id": check_username.id,
        "request_data": request_data,
    }
    token = user_service.get_token(data)
    return Token(access_token=token, token_type="bearer")


@user_router.post(
    "/users/register",
    tags=["Users"],
    status_code=201,
    response_model=UserCreate,
    dependencies=[Depends(UserService.get_current_active_user)],
)
async def create_user(
    user: Annotated[UserCreate, Form()], db: Session = Depends(get_db)
) -> Optional[UserCreate]:
    user_service = UserService(db)
    check_username = user_service.get_username(user.username)
    check_email = user_service.get_email(user.email)
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

    new_user = user_service.create_user(user)
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
#     user_service = UserService(db)
#     existing_roles = user_service._get_roles(roles)

#     if len(existing_roles) != len(roles):
#         raise HTTPException(
#             status_code=400,
#             detail={"error": "Uno o más roles especificados no existen"}
#         )

#     result = user_service.assign_roles(username, existing_roles)
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
#     user_service = UserService(db)
#     check_username = user_service.get_username(username)
#     if not check_username:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail={"error": "Usuario no existe"}
#         )
#     check_currentpass = user_service.verify_password(
#         current_pass, check_username.password
#     )
#     if not check_currentpass:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail={"error": "La contraseña actual no coincide"},
#         )
#     result = user_service.update_password(username, new_pass)
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
