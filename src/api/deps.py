from typing import Annotated, List
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from src.core.database import get_db
from src.core.config import settings
from src.core.security import oauth2_scheme
from src.models.user import User
from src.repositories.user import user_repository

SessionDep = Annotated[AsyncSession, Depends(get_db)]

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], 
    db: SessionDep
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = await user_repository.get_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user

CurrentUserDep = Annotated[User, Depends(get_current_active_user)]

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self, 
        user: CurrentUserDep,
        db: SessionDep
    ) -> User:
        await db.refresh(user, ["roles"])
        user_roles = [role.name for role in user.roles]
        for role in self.allowed_roles:
            if role in user_roles:
                return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
