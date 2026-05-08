from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.user import User
from src.repositories.user import UserRepository
from src.core.security import pwd_context, create_token, create_refresh_token

class AuthService:
    """Business logic for Authentication and Identity."""

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get_tokens(self, user_data: dict) -> dict:
        """Generate access and refresh tokens for a user payload."""
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
        """Verify user credentials and return the user if valid."""
        user = await self.user_repo.get_by_username(db, username)
        if not user:
            return None
        if not pwd_context.verify(password, user.password):
            return None
        
        # Load roles asynchronously to avoid greenlet_spawn error
        await db.refresh(user, ["roles"])
        return user

    def hash_password(self, password: str) -> str:
        """Hash a raw password."""
        return pwd_context.hash(password)

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(password, hashed_password)
