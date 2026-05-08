from src.models.actions import Action
from src.repositories.base import ReadRepositoryMixin

class ActionRepository(ReadRepositoryMixin[Action]):
    """Action-specific repository (Read-only)."""
    async def get_by_name(self, db, name: str):
        from sqlmodel import select
        result = await db.execute(select(Action).where(Action.name == name))
        return result.scalars().first()
