from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import DateTime, Column
from .actions import Action

import uuid
import json

USERS_ID_FOREIGN_KEY = "users.id"


class UserRole(SQLModel, table=True):
    __tablename__ = "user_roles"

    user_id: uuid.UUID = Field(foreign_key=USERS_ID_FOREIGN_KEY, primary_key=True)
    role_id: uuid.UUID = Field(foreign_key="roles.id", primary_key=True)


class Role(SQLModel, table=True):
    __tablename__ = "roles"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=30, unique=True, nullable=False)

    users: List["User"] = Relationship(back_populates="roles", link_model=UserRole)


class UserAuditLog(SQLModel, table=True):
    __tablename__ = "user_audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key=USERS_ID_FOREIGN_KEY, nullable=False)  # Target user
    actor_id: Optional[uuid.UUID] = Field(foreign_key=USERS_ID_FOREIGN_KEY, nullable=True)  # Who did it
    action_id: uuid.UUID = Field(foreign_key="actions.id", nullable=False)
    description: str = Field(nullable=False)
    date: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    # Relationships
    user: "User" = Relationship(
        back_populates="audit_logs", 
        sa_relationship_kwargs={"foreign_keys": "[UserAuditLog.user_id]"}
    )
    actor: Optional["User"] = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[UserAuditLog.actor_id]"}
    )
    action: "Action" = Relationship()


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: Optional[str] = Field(max_length=30, nullable=True)
    surname: Optional[str] = Field(max_length=30, nullable=True)
    username: str = Field(max_length=30, unique=True, nullable=False)
    email: str = Field(max_length=100, unique=True, nullable=False)
    password: str = Field(max_length=100, nullable=False, exclude=True)
    phone: Optional[str] = Field(max_length=20, nullable=True)
    address: Optional[str] = Field(max_length=200, nullable=True)
    picture: Optional[str] = Field(max_length=255, nullable=True)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        sa_type=DateTime(timezone=True),
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    roles: List[Role] = Relationship(back_populates="users", link_model=UserRole)
    audit_logs: List[UserAuditLog] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"foreign_keys": "[UserAuditLog.user_id]"}
    )
