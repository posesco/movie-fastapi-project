from fastapi import HTTPException, APIRouter, Depends, Form, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List

from src.schemas.user import UserCreate
from src.schemas.token import Token
from src.services.user import user_service
from src.api.deps import get_db, get_current_active_user
from src.models.user import User as UserModel

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: AsyncSession = Depends(get_db),
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
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_active_user),
):
    # Note: registration usually requires some permission or is public. 
    # Current logic requires active user.
    check_user = await user_service.authenticate(db, user_in.username, "") # Simplified check
    # Actually better check by username/email directly
    from src.repositories.user import user_repository
    if await user_repository.get_by_username(db, user_in.username):
        raise HTTPException(status_code=409, detail="Username already exists")
    if await user_repository.get_by_email(db, user_in.email):
        raise HTTPException(status_code=409, detail="Email already exists")

    user_model = UserModel(**user_in.model_dump())
    await user_service.create_user(db, user_model)
    return {"success": "User created successfully"}

@router.get("/me", response_model=UserModel)
async def read_users_me(
    current_user: Annotated[UserModel, Depends(get_current_active_user)],
):
    return current_user
