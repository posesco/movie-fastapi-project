from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from config.db import engine
from models import Action
from typing import Optional


class DBService:
    def __init__(self, db=None) -> None:
        self.db = db

    def check_db(self) -> str:
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            return "OK"
        except OperationalError as exec:
            return f"Error: {str(exec)}"
        except Exception as exec:
            return f"Error: {str(exec)}"

    def get_action(self, action: str) -> Optional[Action]:
        return self.db.query(Action).filter(Action.name == action).first()
