from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.models.user import User, Role
from src.repositories.user import UserRepository
from src.services.audit import AuditService

class UserService:
    """Business logic for Users (CRUD and management)."""

    def __init__(self, user_repo: UserRepository, audit_service: AuditService):
        self.user_repo = user_repo
        self.audit_service = audit_service

    async def get_users(self, db: AsyncSession) -> List[User]:
        return await self.user_repo.get_multi(db)

    async def create_user(self, db: AsyncSession, user_in: User, default_role: Optional[str] = None) -> User:
        # Note: Password hashing happens in the API layer or we could inject AuthService here.
        # For now, we'll assume the password is already hashed or use pwd_context directly if we want to keep it simple.
        # But wait, UserService was doing the hashing. Let's keep it doing hashing but maybe via utility.
        from src.core.security import pwd_context
        user_in.password = pwd_context.hash(user_in.password)
        new_user = await self.user_repo.create(db, user_in)
        
        if default_role:
            result = await db.execute(select(Role).where(Role.name == default_role))
            role = result.scalar_one_or_none()
            if role:
                # Refresh with roles to avoid MissingGreenlet when assigning
                await db.refresh(new_user, ["roles"])
                new_user.roles = [role]
                await db.commit()
                await db.refresh(new_user, ["roles"])

        await self.audit_service.log_user_action(db, new_user, "create", "New user created")
        return new_user

    async def assign_roles(self, db: AsyncSession, username: str, roles: List[str], actor: User) -> bool:
        from src.core.config import settings
        
        # Safeguard: Primary admin must always have super_admin role
        if username == settings.admin_user and "super_admin" not in roles:
            return False

        db_user = await self.user_repo.get_by_username(db, username)
        if not db_user or not db_user.is_active:
            return False
        
        result = await db.execute(select(Role).where(Role.name.in_(roles)))
        db_roles = result.scalars().all()
        
        if len(db_roles) != len(roles):
            return False
            
        # Refresh with roles to avoid MissingGreenlet when assigning
        await db.refresh(db_user, ["roles"])
        db_user.roles = db_roles
        
        await self.audit_service.log_user_action(db, db_user, "update", "Assigned roles", actor=actor)
        return True

    async def update_password(self, db: AsyncSession, username: str, new_pass: str, actor: User) -> bool:
        db_user = await self.user_repo.get_by_username(db, username)
        if not db_user:
            return False
        
        from src.core.security import pwd_context
        db_user.password = pwd_context.hash(new_pass)
        await self.audit_service.log_user_action(db, db_user, "update", "Password updated", actor=actor)
        return True

    async def set_user_state(self, db: AsyncSession, user: User, state: bool, actor: User) -> User:
        user.is_active = state
        details = f'The current status is {"enabled" if state else "disabled"}'
        await self.audit_service.log_user_action(db, user, "update", details, actor=actor)
        return user

    async def delete_user(self, db: AsyncSession, username: str, actor: User) -> bool:
        db_user = await self.user_repo.get_by_username(db, username)
        if not db_user:
            return False
        
        db_user.is_active = False
        details = f"User soft-deleted. ID: {db_user.id}, Username: {db_user.username}"
        await self.audit_service.log_user_action(db, db_user, "delete", details, actor=actor)
        return True

    async def update_user(self, db: AsyncSession, db_user: User, update_data: dict, actor: User) -> User:
        if "password" in update_data and update_data["password"]:
            from src.core.security import pwd_context
            update_data["password"] = pwd_context.hash(update_data["password"])
        else:
            # Remove password from dict if it's None or empty to avoid overwriting with None
            update_data.pop("password", None)
            
        updated_user = await self.user_repo.update(db, db_user, update_data)
        
        # Log only changed fields for better audit trail
        details = f"User updated. Fields: {list(update_data.keys())}"
        await self.audit_service.log_user_action(db, updated_user, "update", details, actor=actor)
        return updated_user
