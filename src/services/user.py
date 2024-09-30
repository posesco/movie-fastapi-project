from models.user import User as UserModel
from config.security import create_token
import bcrypt
from dotenv import load_dotenv
from fastapi.encoders import jsonable_encoder
import os

load_dotenv()
ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASS_HASHED = bcrypt.hashpw(
    os.getenv("ADMIN_PASS").encode("utf-8"), bcrypt.gensalt()
)


class UserService:
    def __init__(self, db) -> None:
        self.db = db

    def login_user(self, user):
        if (
            self._verify_password(user.password, ADMIN_PASS_HASHED)
            and user.username == ADMIN_USER
        ):
            return create_token(user.model_dump())
        else:
            db_user = self.get_user(user.username)
            if db_user and self._verify_password(user.password, db_user.password):
                return create_token(user.model_dump())

        return False

    def _verify_password(self, provided_password, stored_password):
        return bcrypt.checkpw(provided_password.encode("utf-8"), stored_password)

    def get_user(self, username):
        return self.db.query(UserModel).filter(UserModel.username == username).first()

    def get_users(self):
        return self.db.query(UserModel).all()

    def create_user(self, user: UserModel):
        if not self.get_user(user.username):
            hashed_password = bcrypt.hashpw(
                user.password.encode("utf-8"), bcrypt.gensalt()
            )
            new_user = UserModel(
                name=user.name or "",
                surname=user.surname or "",
                username=user.username,
                email=user.email,
                password=hashed_password,
            )
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            new_user.log_modification(
                session=self.db,
                action="create",
                description=f"Usuario {new_user.username} creado",
            )
            self.db.commit()
            return True

        return False

    def update_password(self, username: str, current_pass: str, new_pass: str):
        db_user = self.get_user(username)
        if db_user and self._verify_password(current_pass, db_user.password):
            hashed_password = bcrypt.hashpw(new_pass.encode("utf-8"), bcrypt.gensalt())
            db_user.password = hashed_password
            db_user.log_modification(
                session=self.db,
                action="update",
                description=f"Usuario {db_user.username} actualizo su password",
            )
            self.db.commit()
            return True
        return False

    def delete_user(self, username: str):
        db_user = self.get_user(username)
        if db_user:
            db_user.log_modification(
                session=self.db,
                action="delete",
                description=f"Usuario eliminado. {jsonable_encoder(db_user)}",
            )
            self.db.delete(db_user)
            self.db.commit()
            return True
        return False
