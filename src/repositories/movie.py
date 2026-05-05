from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from src.models.movie import Movie
from .base import BaseRepository

class MovieRepository(BaseRepository[Movie]):
    """Movie-specific repository."""
    
    async def get_categories(self, db: AsyncSession) -> List[str]:
        """Get all unique categories."""
        result = await db.execute(select(Movie.category).distinct())
        return result.scalars().all()

movie_repository = MovieRepository(Movie)
