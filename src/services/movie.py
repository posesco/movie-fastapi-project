from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.movie import Movie as MovieModel
from src.models.user import User as UserModel
from src.repositories.movie import movie_repository
from src.services.audit import audit_service

class MovieService:
    """Business logic for Movies."""

    async def get_movies(self, db: AsyncSession) -> List[MovieModel]:
        return await movie_repository.get_multi(db)

    async def get_categories(self, db: AsyncSession) -> List[str]:
        return await movie_repository.get_categories(db)

    async def get_movie(self, db: AsyncSession, id: int) -> Optional[MovieModel]:
        return await movie_repository.get(db, id)

    async def get_movies_by_category(self, db: AsyncSession, category: str) -> List[MovieModel]:
        from sqlmodel import select
        result = await db.execute(select(MovieModel).where(MovieModel.category == category))
        return result.scalars().all()

    async def create_movie(self, db: AsyncSession, movie_in: MovieModel, user: UserModel) -> MovieModel:
        new_movie = await movie_repository.create(db, movie_in)
        
        await audit_service.log_movie_action(
            db, 
            new_movie, 
            "create", 
            f"Movie '{new_movie.title}' created",
            user=user
        )
        
        return new_movie

    async def update_movie(self, db: AsyncSession, id: int, movie_data: dict, user: UserModel) -> Optional[MovieModel]:
        db_obj = await movie_repository.get(db, id)
        if not db_obj:
            return None
        
        updated_movie = await movie_repository.update(db, db_obj, movie_data)
        
        await audit_service.log_movie_action(
            db, 
            updated_movie, 
            "update", 
            f"Movie '{updated_movie.title}' updated",
            user=user
        )
            
        return updated_movie

    async def delete_movie(self, db: AsyncSession, id: int, user: UserModel) -> bool:
        db_obj = await movie_repository.get(db, id)
        if not db_obj:
            return False
        
        movie_title = db_obj.title
        
        # User audit log for movie deletion
        await audit_service.log_user_action(
            db, 
            user, 
            "delete", 
            f"User deleted movie '{movie_title}' (ID: {id})"
        )
            
        return await movie_repository.delete(db, id)

movie_service = MovieService()
