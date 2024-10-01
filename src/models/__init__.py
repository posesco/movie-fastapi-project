from config.db import Base, engine
from .actions import Action
from .user import Role, User, UserAuditLog
from .movie import Movie, MovieAuditLog

__all__ = ["Action", "Role", "User", "UserAuditLog", "Movie", "MovieAuditLog"]


def init_db():
    Base.metadata.create_all(bind=engine)
