from typing import Generic, TypeVar, Type, Optional, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlmodel import SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)

class BaseRepository(Generic[ModelType]):
    """Base repository for CRUD operations using SQLModel and AsyncSession."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

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

    async def create(self, db: AsyncSession, obj_in: ModelType) -> ModelType:
        """Create a new record."""
        db.add(obj_in)
        await db.flush()
        await db.refresh(obj_in)
        return obj_in

    async def update(
        self, 
        db: AsyncSession, 
        db_obj: ModelType, 
        obj_in: dict
    ) -> ModelType:
        """Update an existing record."""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: Any) -> bool:
        """Delete a record by ID."""
        obj = await self.get(db, id)
        if obj:
            await db.delete(obj)
            return True
        return False
