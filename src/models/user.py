from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, timezone

import uuid
import json


class UserRole(SQLModel, table=True):
    __tablename__ = "user_roles"

    user_id: uuid.UUID = Field(foreign_key="users.id", primary_key=True)
    role_id: uuid.UUID = Field(foreign_key="roles.id", primary_key=True)


class Role(SQLModel, table=True):
    __tablename__ = "roles"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=30, unique=True, nullable=False)

    users: List["User"] = Relationship(back_populates="roles", link_model=UserRole)


class UserAuditLog(SQLModel, table=True):
    __tablename__ = "user_audit_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    action_id: uuid.UUID = Field(foreign_key="actions.id", nullable=False)
    description: str = Field(nullable=False)
    date: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: Optional[str] = Field(max_length=30, nullable=True)
    surname: Optional[str] = Field(max_length=30, nullable=True)
    username: str = Field(max_length=30, unique=True, nullable=False)
    email: str = Field(max_length=100, unique=True, nullable=False)
    password: str = Field(max_length=100, nullable=False)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), nullable=False
    )

    roles: List[Role] = Relationship(back_populates="users", link_model=UserRole)

    def log_modification(self, session, action_id: str, description: dict):
        log_entry = UserAuditLog(
            user_id=self.id,
            action_id=action_id,
            description=json.dumps(description),
        )
        session.add(log_entry)
