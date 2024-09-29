from models.user import User as UserModel
from config.security import create_token
import bcrypt
from dotenv import load_dotenv
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
            db_user = self._get_db_user(user.username)
            if db_user and self._verify_password(user.password, db_user.password):
                return create_token(user.model_dump())

        return False

    def _verify_password(self, provided_password, stored_password):
        return bcrypt.checkpw(provided_password.encode("utf-8"), stored_password)

    def _get_db_user(self, username):
        return self.db.query(UserModel).filter(UserModel.username == username).first()

    def create_user(self, user: UserModel):
        if not self._get_db_user(user.username):
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
            return new_user

        return False

    def update_password(self, username, new_pass):
        new_pass = (
            self.db.query(UserModel).filter(UserModel.username == username).first()
        )
        hashed_password = bcrypt.hashpw(new_pass.encode("utf-8"), bcrypt.gensalt())
        new_pass.password = hashed_password
        new_pass.action = "update"
        new_pass.description = "Password actualizado"
        self.db.commit()
        return new_pass

    def delete_user(self, id):
        result = self.db.query(UserModel).filter(UserModel.id == id).first()
        self.db.delete(result)
        self.db.commit()
        return result

    def get_users(self):
        result = self.db.query(UserModel).all()
        return result

    def get_user(self, username):
        result = self.db.query(UserModel).filter(UserModel.username == username).first()
        return result
