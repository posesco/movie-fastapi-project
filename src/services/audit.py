from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from src.models.user import UserAuditLog, User
from src.models.movie import MovieAuditLog, Movie
from src.models.actions import Action
from src.repositories.audit import AuditRepository
from src.repositories.action import ActionRepository

class AuditService:
    """Service to handle business auditing logic."""
    
    def __init__(self, action_repo: ActionRepository, audit_repo: AuditRepository):
        self.action_repo = action_repo
        self.audit_repo = audit_repo
    
    async def _get_action(self, db: AsyncSession, action_name: str) -> Action:
        action = await self.action_repo.get_by_name(db, action_name)
        if not action:
            # Fallback to 'update' if specific action not found
            action_result = await db.execute(select(Action).where(Action.name == "update"))
            action = action_result.scalar_one_or_none()
        return action

    async def log_user_action(
        self, 
        db: AsyncSession, 
        user: User, 
        action_name: str, 
        details: str
    ) -> None:
        action = await self._get_action(db, action_name)
        if not action: return

        log_entry = UserAuditLog(
            user_id=user.id,
            action_id=action.id,
            description=f"User {user.username} performed {action_name}: {details}",
        )
        db.add(log_entry)

    async def log_movie_action(
        self,
        db: AsyncSession,
        movie: Movie,
        action_name: str,
        details: str,
        user: User = None
    ) -> None:
        action = await self._get_action(db, action_name)
        if not action: return

        # Movie audit
        movie_log = MovieAuditLog(
            movie_id=movie.id,
            action_id=action.id,
            description=details,
        )
        db.add(movie_log)

        # Optional: Log which user performed the action on the movie
        if user:
            user_log = UserAuditLog(
                user_id=user.id,
                action_id=action.id,
                description=f"User {user.username} {action_name} movie '{movie.title}' (ID: {movie.id})"
            )
            db.add(user_log)
