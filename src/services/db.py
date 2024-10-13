from sqlmodel import Session, select
from config.db import engine
from models.actions import Action
from typing import Optional


class DBService:
    def __init__(self, db=None) -> None:
        self.db = db

    def check_db(self) -> str:
        try:
            with Session(engine) as session:
                session.exec(select(1))
            return "OK"
        except Exception as exec:
            return f"Error: {str(exec)}"

    def get_action(self, action: str) -> Optional[Action]:
        return self.db.query(Action).filter(Action.name == action).first()
