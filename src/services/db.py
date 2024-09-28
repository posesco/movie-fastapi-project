from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from config.db import engine


def check_db():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return "OK"
    except OperationalError as exec:
        return f"Error: {str(exec)}"
    except Exception as exec:
        return f"Error: {str(exec)}"
