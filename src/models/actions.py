from sqlalchemy import Column, event, String
from sqlalchemy.orm import Session
from config.db import Base
import uuid


class Action(Base):
    __tablename__ = "actions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(30), unique=True, nullable=False)


def insert_default_actions(target, connection, **kwargs):
    actions = ["create", "update", "delete"]
    session = Session(bind=connection)
    for action_name in actions:
        action = Action(name=action_name)
        session.add(action)
    session.commit()


event.listen(Action.__table__, "after_create", insert_default_actions)
