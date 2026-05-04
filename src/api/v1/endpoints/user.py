from fastapi import HTTPException, APIRouter, Depends, Form, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, List

from src.schemas.user import UserCreate, UserRoleAssign, UserUpdate, UserRead, UserAuditLogRead
from src.schemas.token import Token, RefreshTokenRequest
from src.services.user import user_service
from src.api.deps import SessionDep, CurrentUserDep, RoleChecker
from src.models.user import User as UserModel
from src.core.redis import blacklist_token, is_token_blacklisted
from src.core.security import oauth2_scheme, pwd_context
from src.core.config import settings
import jwt
import datetime

from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix="/user", tags=["Users"])

@router.post("/refresh", response_model=Token)
async def refresh_token(
    data: RefreshTokenRequest,
    db: SessionDep,
) -> Token:
    try:
        payload = jwt.decode(
            data.refresh_token, settings.secret_key, algorithms=[settings.algorithm]
        )
        username: str = payload.get("sub")
        jti: str = payload.get("jti")
        if username is None or jti is None:
            raise HTTPException(status_code=401, detail="Invalid refresh token")
            
        # Check if blacklisted
        if await is_token_blacklisted(jti):
            raise HTTPException(status_code=401, detail="Refresh token has been revoked")
            
        from src.repositories.user import user_repository
        user = await user_repository.get_by_username(db, username)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        await db.refresh(user, ["roles"])
        user_info = {
            "id": str(user.id),
            "roles": [str(role.id) for role in user.roles],
        }
        new_data = {
            "sub": user.username,
            "user_info": user_info,
        }
        tokens = await user_service.get_tokens(new_data)
        
        # Blacklist the old refresh token
        exp = payload.get("exp")
        now = datetime.datetime.now(datetime.timezone.utc).timestamp()
        remaining = int(exp - now)
        if remaining > 0:
            await blacklist_token(jti, remaining)
            
        return Token(**tokens)
        
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@router.post("/logout")
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> dict:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        jti = payload.get("jti")
        exp = payload.get("exp")
        if jti and exp:
            # Calculate remaining time for the token
            import datetime
            now = datetime.datetime.now(datetime.timezone.utc).timestamp()
            remaining = int(exp - now)
            if remaining > 0:
                await blacklist_token(jti, remaining)
    except jwt.PyJWTError:
        pass  # Token is already invalid
        
    return {"success": "Logged out successfully"}

@router.post("/login", response_model=Token, dependencies=[Depends(RateLimiter(times=5, seconds=60))])
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
    tokens = await user_service.get_tokens(data)
    return Token(**tokens)

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

@router.put("/assign-roles", dependencies=[Depends(RoleChecker(["super_admin", "admin"]))])
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

@router.delete("/{username}", dependencies=[Depends(RoleChecker(["super_admin", "admin"]))])
async def delete_user(
    username: str,
    db: SessionDep,
) -> dict:
    from src.core.config import settings
    if username == settings.admin_user:
        raise HTTPException(
            status_code=403, 
            detail="Cannot delete the primary super_admin account"
        )

    from src.repositories.user import user_repository
    db_user = await user_repository.get_by_username(db, username)
    if not db_user:
        raise HTTPException(status_code=404, detail=f"User {username} not found")
    
    # Check if user has super_admin role
    await db.refresh(db_user, ["roles"])
    if any(role.name == "super_admin" for role in db_user.roles):
        raise HTTPException(
            status_code=403, 
            detail="Cannot delete a user with super_admin role"
        )

    success = await user_service.delete_user(db, username)
    if not success:
        raise HTTPException(status_code=400, detail="Failed to delete user")

    return {"success": f"User {username} deleted successfully"}

@router.get("/me", response_model=UserRead)
async def read_users_me(
    current_user: CurrentUserDep,
    db: SessionDep,
) -> UserModel:
    await db.refresh(current_user, ["roles"])
    return current_user


@router.get("/", response_model=List[UserRead], dependencies=[Depends(RoleChecker(["super_admin", "admin"]))])
async def list_users(
    db: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> List[UserModel]:
    """
    List all users with pagination.
    Accessible only by super_admin and admin roles.
    """
    from src.repositories.user import user_repository
    users = await user_repository.get_multi(db, skip=skip, limit=limit)
    
    # Eagerly load roles for each user to avoid N+1 queries in the response model serialization
    for user in users:
        await db.refresh(user, ["roles"])
    return users


@router.get("/{username}/activity", response_model=List[UserAuditLogRead], dependencies=[Depends(RoleChecker(["super_admin", "admin"]))])
async def get_user_activity(
    username: str,
    db: SessionDep,
    skip: int = 0,
    limit: int = 100,
) -> List[UserAuditLogRead]:
    """
    Get activity logs for a specific user.
    Accessible only by super_admin and admin roles.
    """
    from src.repositories.user import user_repository
    from src.repositories.audit import audit_repository
    
    db_user = await user_repository.get_by_username(db, username)
    if not db_user:
        raise HTTPException(status_code=404, detail=f"User {username} not found")
        
    activity = await audit_repository.get_by_user_id(
        db, 
        user_id=db_user.id, 
        skip=skip, 
        limit=limit
    )
    
    # Ensure action relationship is loaded for each log entry
    for log in activity:
        await db.refresh(log, ["action"])
        
    return [UserAuditLogRead.from_orm_with_action(log) for log in activity]


@router.put("/{username}", response_model=UserRead)
async def update_user(
    username: str,
    user_update: UserUpdate,
    db: SessionDep,
    current_user: CurrentUserDep,
) -> UserModel:
    from src.repositories.user import user_repository
    target_user = await user_repository.get_by_username(db, username)
    if not target_user:
        raise HTTPException(status_code=404, detail=f"User {username} not found")

    # Refresh roles for RBAC checks
    await db.refresh(current_user, ["roles"])
    await db.refresh(target_user, ["roles"])

    current_roles = {role.name for role in current_user.roles}
    target_roles = {role.name for role in target_user.roles}

    # RBAC Logic
    authorized = False

    if "super_admin" in current_roles:
        authorized = True
    elif "admin" in current_roles:
        if "super_admin" in target_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admins cannot edit super_admin users"
            )
        authorized = True
    elif "editor" in current_roles or "user" in current_roles:
        if current_user.id == target_user.id:
            authorized = True
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only edit your own profile"
            )

    if not authorized:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    # Password confirmation logic
    if user_update.password:
        is_privileged = any(role in current_roles for role in ["super_admin", "admin"])
        if not is_privileged:
            if not user_update.current_password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Current password is required to change password"
                )
            if not pwd_context.verify(user_update.current_password, target_user.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid current password"
                )

    # Email uniqueness check if email is being updated
    if user_update.email and user_update.email != target_user.email:
        if await user_repository.get_by_email(db, user_update.email):
            raise HTTPException(status_code=409, detail="Email already exists")

    update_data = user_update.model_dump(exclude_unset=True)
    update_data.pop("current_password", None)
    updated_user = await user_service.update_user(db, target_user, update_data)
    await db.refresh(updated_user, ["roles"])
    return updated_user
