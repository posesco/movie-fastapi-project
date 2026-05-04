from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from src.models.user import UserAuditLog
from src.repositories.base import BaseRepository
import uuid

class AuditRepository(BaseRepository[UserAuditLog]):
    """Audit Log specific repository."""
    
    async def get_by_user_id(
        self, 
        db: AsyncSession, 
        user_id: uuid.UUID, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[UserAuditLog]:
        """Get audit logs for a specific user."""
        result = await db.execute(
            select(UserAuditLog)
            .where(UserAuditLog.user_id == user_id)
            .order_by(UserAuditLog.date.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

audit_repository = AuditRepository(UserAuditLog)
