from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.movie import Movie as MovieModel
from src.models.user import User as UserModel, UserAuditLog
from src.repositories.movie import movie_repository
from src.repositories.action import action_repository

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
        
        # Audit logs
        action = await action_repository.get_by_name(db, "create")
        if action:
            # Movie audit
            new_movie.log_modification(db, action.id, f"Movie '{new_movie.title}' created")
            # User audit
            user_log = UserAuditLog(
                user_id=user.id,
                action_id=action.id,
                description=f"User created movie '{new_movie.title}' (ID: {new_movie.id})"
            )
            db.add(user_log)
        
        return new_movie

    async def update_movie(self, db: AsyncSession, id: int, movie_data: dict, user: UserModel) -> Optional[MovieModel]:
        db_obj = await movie_repository.get(db, id)
        if not db_obj:
            return None
        
        updated_movie = await movie_repository.update(db, db_obj, movie_data)
        
        # Audit logs
        action = await action_repository.get_by_name(db, "update")
        if action:
            # Movie audit
            updated_movie.log_modification(db, action.id, f"Movie '{updated_movie.title}' updated")
            # User audit
            user_log = UserAuditLog(
                user_id=user.id,
                action_id=action.id,
                description=f"User updated movie '{updated_movie.title}' (ID: {updated_movie.id})"
            )
            db.add(user_log)
            
        return updated_movie

    async def delete_movie(self, db: AsyncSession, id: int, user: UserModel) -> bool:
        db_obj = await movie_repository.get(db, id)
        if not db_obj:
            return False
        
        movie_title = db_obj.title
        action = await action_repository.get_by_name(db, "delete")
        
        # User audit (must be done before delete or capture ID)
        if action:
            user_log = UserAuditLog(
                user_id=user.id,
                action_id=action.id,
                description=f"User deleted movie '{movie_title}' (ID: {id})"
            )
            db.add(user_log)
            
        return await movie_repository.delete(db, id)

movie_service = MovieService()
