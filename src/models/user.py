from sqlalchemy import (
    Integer,
    Column,
    Enum,
    String,
    DateTime,
    ForeignKey,
)
from config.db import Base
from datetime import datetime
import uuid
import enum


class ActionEnum(enum.Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class UserAuditLog(Base):
    __tablename__ = "user_audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    action = Column(Enum(ActionEnum), nullable=False)
    description = Column(String(300))
    date = Column(DateTime, default=lambda: datetime.now(), nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(200), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(), nullable=False)
    last_update = Column(DateTime, default=lambda: datetime.now(), nullable=False)

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
