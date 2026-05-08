from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlmodel import SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)

class Repository(Generic[ModelType]):
    """Common base for all repositories to hold the model type."""
    def __init__(self, model: Type[ModelType]):
        self.model = model

class ReadRepositoryMixin(Repository[ModelType]):
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

class CreateRepositoryMixin(Repository[ModelType]):
    """Mixin for create operations."""
    async def create(self, db: AsyncSession, obj_in: ModelType) -> ModelType:
        """Create a new record."""
        db.add(obj_in)
        await db.flush()
        await db.refresh(obj_in)
        return obj_in

class UpdateRepositoryMixin(Repository[ModelType]):
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

class DeleteRepositoryMixin(Repository[ModelType]):
    """Mixin for delete operations."""
    async def delete(self, db: AsyncSession, id: Any) -> bool:
        """Delete a record by ID."""
        # Note: This uses 'get' which is in ReadRepositoryMixin. 
        # If a repo only has Delete but not Read, this will fail.
        # Usually Delete implies Read access or we can use a direct delete query.
        # For simplicity in this project, we assume Delete repositories also have Read.
        result = await db.execute(
            select(self.model).where(self.model.id == id)
        )
        obj = result.scalars().first()
        if obj:
            await db.delete(obj)
            return True
        return False

class BaseRepository(
    ReadRepositoryMixin[ModelType],
    CreateRepositoryMixin[ModelType],
    UpdateRepositoryMixin[ModelType],
    DeleteRepositoryMixin[ModelType]
):
    """Full CRUD repository."""
    pass
