from typing import Type, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlmodel import SQLModel


class Repository[ModelType: SQLModel]:
    """Common base for all repositories to hold the model type."""
    def __init__(self, model: Type[ModelType]):
        self.model = model

class ReadRepositoryMixin[ModelType: SQLModel](Repository[ModelType]):
    """Mixin for read operations."""
    async def count(self, db: AsyncSession) -> int:
        """Count total records."""
        result = await db.execute(select(func.count()).select_from(self.model))
        return result.scalar() or 0

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """Get a single record by ID."""
        result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalars().first()

    async def get_multi(
        self, 
        db: AsyncSession, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[ModelType]:
        """Get multiple records with pagination."""
        result = await db.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return result.scalars().all()

class CreateRepositoryMixin[ModelType: SQLModel](Repository[ModelType]):
    """Mixin for create operations."""
    async def create(self, db: AsyncSession, obj_in: ModelType) -> ModelType:
        """Create a new record."""
        db.add(obj_in)
        await db.flush()
        await db.refresh(obj_in)
        return obj_in

class UpdateRepositoryMixin[ModelType: SQLModel](Repository[ModelType]):
    """Mixin for update operations."""
    async def update(
        self, 
        db: AsyncSession, 
        db_obj: ModelType, 
        obj_in: dict
    ) -> ModelType:
        """Update an existing record."""
        for field, value in obj_in.items():
            if field == "id":
                continue
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

class DeleteRepositoryMixin[ModelType: SQLModel](Repository[ModelType]):
    """Mixin for delete operations."""
    async def delete(self, db: AsyncSession, id: Any) -> bool:
        """Delete a record by ID."""
        result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        obj = result.scalars().first()
        if obj:
            await db.delete(obj)
            return True
        return False

class BaseRepository[ModelType: SQLModel](
    ReadRepositoryMixin[ModelType],
    CreateRepositoryMixin[ModelType],
    UpdateRepositoryMixin[ModelType],
    DeleteRepositoryMixin[ModelType]
):
    """Full CRUD repository."""
    pass
