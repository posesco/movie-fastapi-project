from fastapi import HTTPException, APIRouter, Depends, Form, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List

from src.schemas.user import UserCreate, UserRoleAssign
from src.schemas.token import Token
from src.services.user import user_service
from src.api.deps import SessionDep, CurrentUserDep, RoleChecker
from src.models.user import User as UserModel

router = APIRouter(prefix="/user", tags=["Users"])

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: SessionDep,
) -> Token:
    user = await user_service.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_info = {
        "id": str(user.id),
        "roles": [str(role.id) for role in user.roles],
        "client_ip": request.client.host,
        "url": str(request.url),
    }
    data = {
        "sub": user.username,
        "user_info": user_info,
    }
    token = await user_service.get_token(data)
    return Token(access_token=token, token_type="bearer")

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(
    user_in: Annotated[UserCreate, Form()],
    db: SessionDep,
) -> dict:
    from src.repositories.user import user_repository
    if await user_repository.get_by_username(db, user_in.username):
        raise HTTPException(status_code=409, detail="Username already exists")
    if await user_repository.get_by_email(db, user_in.email):
        raise HTTPException(status_code=409, detail="Email already exists")

    user_model = UserModel(**user_in.model_dump())
    await user_service.create_user(db, user_model, default_role="user")
    return {"success": "User created successfully"}

@router.post("/assign-roles", dependencies=[Depends(RoleChecker(["super_admin", "admin"]))])
async def assign_user_roles(
    data: UserRoleAssign,
    db: SessionDep,
) -> dict:
    from src.repositories.user import user_repository
    db_user = await user_repository.get_by_username(db, data.username)
    if not db_user:
        raise HTTPException(status_code=404, detail=f"User {data.username} not found")
    
    success = await user_service.assign_roles(db, data.username, data.roles)
    if not success:
        raise HTTPException(status_code=400, detail="One or more roles do not exist in database")
        
    return {"success": f"Roles {data.roles} assigned to {data.username}"}

@router.get("/me", response_model=UserModel)
async def read_users_me(
    current_user: CurrentUserDep,
) -> UserModel:
    return current_user
