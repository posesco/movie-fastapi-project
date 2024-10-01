from sqlalchemy import (
    Integer,
    Column,
    event,
    String,
    Table,
    Boolean,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship, Session
from config.db import Base
from datetime import datetime, timezone
import uuid

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", String, ForeignKey("users.id"), primary_key=True),
    Column("role_id", String, ForeignKey("roles.id"), primary_key=True),
)

user_actions = Table(
    "user_actions",
    Base.metadata,
    Column("user_id", String, ForeignKey("users.id"), primary_key=True),
    Column("action_id", String, ForeignKey("actions.id"), primary_key=True),
)


class Role(Base):
    __tablename__ = "roles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(30), unique=True, nullable=False)


def insert_default_roles(target, connection, **kwargs):
    roles = ["admin", "editor", "user"]
    session = Session(bind=connection)
    for role_name in roles:
        role = Role(name=role_name)
        session.add(role)
    session.commit()


event.listen(Role.__table__, "after_create", insert_default_roles)


class UserAuditLog(Base):
    __tablename__ = "user_audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    action_id = Column(String, ForeignKey("actions.id"), nullable=False)
    description = Column(String(300))
    date = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(30), nullable=True)
    surname = Column(String(30), nullable=True)
    username = Column(String(30), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    roles = relationship("Role", secondary=user_roles, backref="users")

    def log_modification(self, session, action, description):
        if action not in ["create", "update", "delete"]:
            raise ValueError(
                "Acción no válida: debe ser 'create', 'update', or 'delete'"
            )
        log_entry = UserAuditLog(
            user_id=self.id,
            action=action,
            description=description,
        )
        session.add(log_entry)
