from sqlalchemy import Column, ForeignKey, DateTime, Integer, String, Float
from config.db import Base
from datetime import datetime, timezone


class MovieAuditLog(Base):
    __tablename__ = "movie_audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_id = Column(String, ForeignKey("movies.id"), nullable=False)
    action_id = Column(String, ForeignKey("actions.id"), nullable=False)
    description = Column(String(300))
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(100), unique=True, nullable=False)
    overview = Column(String(350), nullable=False)
    year = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)
    category = Column(String(30), nullable=False)
    director = Column(String(30), nullable=False)
    studio = Column(String(60), nullable=False)
    box_office = Column(Integer, nullable=False)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    def log_modification(self, session, action_id, description):
        log_entry = MovieAuditLog(
            movie_id=self.id,
            action_id=action_id,
            description=description,
        )
        session.add(log_entry)
