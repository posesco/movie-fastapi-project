from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from src.models.user import User
from .base import BaseRepository

class UserRepository(BaseRepository[User]):
    """User-specific repository with extra query methods."""

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username."""
        result = await db.execute(select(User).where(User.username == username))
        return result.scalars().first()

user_repository = UserRepository(User)
