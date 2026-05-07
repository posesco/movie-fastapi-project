from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.user import User, Role
from src.repositories.user import user_repository
from src.services.audit import audit_service
from src.core.security import pwd_context, create_token, create_refresh_token

class UserService:
    """Business logic for Users."""

    async def get_tokens(self, user_data: dict) -> dict:
        access_token = create_token(user_data)
        refresh_token = create_refresh_token(user_data)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    async def authenticate(
        self, db: AsyncSession, username: str, password: str
    ) -> Optional[User]:
        user = await user_repository.get_by_username(db, username)
        if not user:
            return None
        if not pwd_context.verify(password, user.password):
            return None
        
        # Load roles asynchronously to avoid greenlet_spawn error
        await db.refresh(user, ["roles"])
        return user

    async def get_users(self, db: AsyncSession) -> List[User]:
        return await user_repository.get_multi(db)

    async def create_user(self, db: AsyncSession, user_in: User, default_role: Optional[str] = None) -> User:
        user_in.password = pwd_context.hash(user_in.password)
        new_user = await user_repository.create(db, user_in)
        
        if default_role:
            result = await db.execute(select(Role).where(Role.name == default_role))
            role = result.scalar_one_or_none()
            if role:
                # Refresh with roles to avoid MissingGreenlet when assigning
                await db.refresh(new_user, ["roles"])
                new_user.roles = [role]
                await db.commit()
                await db.refresh(new_user, ["roles"])

        await audit_service.log_user_action(db, new_user, "create", "New user created")
        return new_user

    async def assign_roles(self, db: AsyncSession, username: str, roles: List[str]) -> bool:
        db_user = await user_repository.get_by_username(db, username)
        if not db_user:
            return False
        
        result = await db.execute(select(Role).where(Role.name.in_(roles)))
        db_roles = result.scalars().all()
        
        if len(db_roles) != len(roles):
            return False
            
        # Refresh with roles to avoid MissingGreenlet when assigning
        await db.refresh(db_user, ["roles"])
        db_user.roles = db_roles
        
        await audit_service.log_user_action(db, db_user, "update", "Assigned roles")
        return True

    async def update_password(self, db: AsyncSession, username: str, new_pass: str) -> bool:
        db_user = await user_repository.get_by_username(db, username)
        if not db_user:
            return False
        
        db_user.password = pwd_context.hash(new_pass)
        await audit_service.log_user_action(db, db_user, "update", "Password updated")
        return True

    async def set_user_state(self, db: AsyncSession, user: User, state: bool) -> User:
        user.is_active = state
        details = f'The current status is {"enabled" if state else "disabled"}'
        await audit_service.log_user_action(db, user, "update", details)
        return user

    async def delete_user(self, db: AsyncSession, username: str) -> bool:
        db_user = await user_repository.get_by_username(db, username)
        if not db_user:
            return False
        
        db_user.is_active = False
        details = f"User soft-deleted. ID: {db_user.id}, Username: {db_user.username}"
        await audit_service.log_user_action(db, db_user, "delete", details)
        return True

    async def update_user(self, db: AsyncSession, db_user: User, update_data: dict) -> User:
        if "password" in update_data and update_data["password"]:
            update_data["password"] = pwd_context.hash(update_data["password"])
        else:
            # Remove password from dict if it's None or empty to avoid overwriting with None
            update_data.pop("password", None)
            
        updated_user = await user_repository.update(db, db_user, update_data)
        
        # Log only changed fields for better audit trail
        details = f"User updated. Fields: {list(update_data.keys())}"
        await audit_service.log_user_action(db, updated_user, "update", details)
        return updated_user

user_service = UserService()
