from src.models.actions import Action
from src.repositories.base import BaseRepository

class ActionRepository(BaseRepository[Action]):
    """Action-specific repository."""
    async def get_by_name(self, db, name: str):
        from sqlmodel import select
        result = await db.execute(select(Action).where(Action.name == name))
        return result.scalars().first()

action_repository = ActionRepository(Action)
