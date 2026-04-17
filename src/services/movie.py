from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.movie import Movie as MovieModel
from src.repositories.movie import movie_repository

class MovieService:
    """Business logic for Movies."""

    async def get_movies(self, db: AsyncSession) -> List[MovieModel]:
        return await movie_repository.get_multi(db)

    async def get_movie(self, db: AsyncSession, id: int) -> Optional[MovieModel]:
        return await movie_repository.get(db, id)

    async def get_movies_by_category(self, db: AsyncSession, category: str) -> List[MovieModel]:
        from sqlmodel import select
        result = await db.execute(select(MovieModel).where(MovieModel.category == category))
        return result.scalars().all()

    async def create_movies(self, db: AsyncSession, movies_in: List[MovieModel]) -> List[MovieModel]:
        for movie in movies_in:
            await movie_repository.create(db, movie)
        return movies_in

    async def update_movie(self, db: AsyncSession, id: int, movie_data: dict) -> Optional[MovieModel]:
        db_obj = await movie_repository.get(db, id)
        if not db_obj:
            return None
        return await movie_repository.update(db, db_obj, movie_data)

    async def delete_movie(self, db: AsyncSession, id: int) -> bool:
        return await movie_repository.delete(db, id)

movie_service = MovieService()
