from typing import Annotated, List, Type
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
from src.core.database import get_db
from src.core.config import settings
from src.core.security import oauth2_scheme
from src.core.redis import is_token_blacklisted
from src.models.user import User as UserModel, UserAuditLog
from src.models.movie import Movie as MovieModel
from src.models.actions import Action as ActionModel
from src.repositories.user import UserRepository
from src.repositories.movie import MovieRepository
from src.repositories.action import ActionRepository
from src.repositories.audit import AuditRepository
from src.services.audit import AuditService
from src.services.user import UserService
from src.services.movie import MovieService
from src.services.auth import AuthService
from src.services.storage.base import StorageProvider
from src.services.storage.s3 import S3StorageProvider

SessionDep = Annotated[AsyncSession, Depends(get_db)]

# Repository Providers
def get_user_repository() -> UserRepository:
    return UserRepository(UserModel)

def get_movie_repository() -> MovieRepository:
    return MovieRepository(MovieModel)

def get_action_repository() -> ActionRepository:
    return ActionRepository(ActionModel)

def get_audit_repository() -> AuditRepository:
    return AuditRepository(UserAuditLog)

# Service Providers
def get_audit_service(
    action_repo: ActionRepository = Depends(get_action_repository),
    audit_repo: AuditRepository = Depends(get_audit_repository)
) -> AuditService:
    return AuditService(action_repo, audit_repo)

def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    audit_service: AuditService = Depends(get_audit_service)
) -> UserService:
    return UserService(user_repo, audit_service)

def get_movie_service(
    movie_repo: MovieRepository = Depends(get_movie_repository),
    audit_service: AuditService = Depends(get_audit_service)
) -> MovieService:
    return MovieService(movie_repo, audit_service)

def get_auth_service(
    user_repo: UserRepository = Depends(get_user_repository)
) -> AuthService:
    return AuthService(user_repo)

def get_storage_provider() -> StorageProvider:
    if settings.storage_backend == "s3":
        return S3StorageProvider()
    else:
        from src.services.storage.local import LocalStorageProvider
        return LocalStorageProvider()

# Annotated Service Dependencies
UserServiceDep = Annotated[UserService, Depends(get_user_service)]
MovieServiceDep = Annotated[MovieService, Depends(get_movie_service)]
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
StorageProviderDep = Annotated[StorageProvider, Depends(get_storage_provider)]

async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)], 
    db: SessionDep,
    user_repo: UserRepository = Depends(get_user_repository)
) -> UserModel:
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
        jti: str = payload.get("jti")
        if username is None or jti is None:
            raise credentials_exception
        
        # Check if token is blacklisted in Redis
        if await is_token_blacklisted(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = await user_repo.get_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[UserModel, Depends(get_current_user)],
) -> UserModel:
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    return current_user

CurrentUserDep = Annotated[UserModel, Depends(get_current_active_user)]

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    async def __call__(
        self, 
        user: CurrentUserDep,
        db: SessionDep
    ) -> UserModel:
        await db.refresh(user, ["roles"])
        user_roles = [role.name for role in user.roles]
        for role in self.allowed_roles:
            if role in user_roles:
                return user
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges",
        )
