import json
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from fastapi.encoders import jsonable_encoder

from src.models.user import User, Role, UserAuditLog
from src.repositories.user import user_repository
from src.repositories.action import action_repository
from src.core.security import pwd_context, create_token

class UserService:
    """Business logic for Users."""

    async def _log_modification(
        self, db: AsyncSession, user: User, user_action: str, details: str
    ) -> None:
        action = await action_repository.get_by_name(db, user_action)
        if not action:
            # Fallback if action doesn't exist to avoid AttributeError
            from src.models.actions import Action
            action_result = await db.execute(select(Action).where(Action.name == "update"))
            action = action_result.scalar_one_or_none()
            if not action:
                return # Can't log if no actions exist

        description_data = {
            "user": user.username,
            "action": user_action,
            "details": details,
        }
        log_entry = UserAuditLog(
            user_id=user.id,
            action_id=action.id,
            description=json.dumps(description_data),
        )
        db.add(log_entry)

    async def get_token(self, user_data: dict) -> str:
        return create_token(user_data)

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

        await self._log_modification(db, new_user, "create", "New user created")
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
        
        await self._log_modification(db, db_user, "update", "Assigned roles")
        return True

    async def update_password(self, db: AsyncSession, username: str, new_pass: str) -> bool:
        db_user = await user_repository.get_by_username(db, username)
        if not db_user:
            return False
        
        db_user.password = pwd_context.hash(new_pass)
        await self._log_modification(db, db_user, "update", "Password updated")
        return True

    async def set_user_state(self, db: AsyncSession, user: User, state: bool) -> User:
        user.is_active = state
        details = f'The current status is {"enabled" if state else "disabled"}'
        await self._log_modification(db, user, "update", details)
        return user

    async def delete_user(self, db: AsyncSession, username: str) -> bool:
        db_user = await user_repository.get_by_username(db, username)
        if not db_user:
            return False
        
        details = f"User deleted. {jsonable_encoder(db_user)}"
        await self._log_modification(db, db_user, "update", details)
        await db.delete(db_user)
        return True

user_service = UserService()
