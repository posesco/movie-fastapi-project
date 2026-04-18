from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import DateTime, BigInteger
import uuid


class MovieAuditLog(SQLModel, table=True):
    __tablename__ = "movie_audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    movie_id: int = Field(foreign_key="movies.id", nullable=False)
    action_id: uuid.UUID = Field(foreign_key="actions.id", nullable=False)
    description: Optional[str] = Field(default=None, max_length=300)
    date: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class Movie(SQLModel, table=True):
    __tablename__ = "movies"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(max_length=100, unique=True, nullable=False)
    overview: str = Field(max_length=350, nullable=False)
    year: int = Field(nullable=False)
    rating: float = Field(nullable=False)
    category: str = Field(max_length=30, nullable=False)
    director: str = Field(max_length=30, nullable=False)
    studio: str = Field(max_length=60, nullable=False)
    box_office: int = Field(sa_type=BigInteger, nullable=False)
    created_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    def log_modification(self, session, action_id, description):
        log_entry = MovieAuditLog(
            movie_id=self.id,
            action_id=action_id,
            description=description,
        )
        session.add(log_entry)
