from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from typing import Optional
from models import User as UserModel, Role
from config.security import create_token
from services.db import DBService
import bcrypt


class UserService:
    def __init__(self, db) -> None:
        self.db = db

    def _log_modification(
        self, user: UserModel, user_action: str, details: str
    ) -> None:
        action = DBService(self.db).get_action(user_action)
        description_data = {
            "user": user.username,
            "action": user_action,
            "details": details,
        }
        user.log_modification(
            session=self.db,
            action_id=action.id,
            description=description_data,
        )
        self.db.commit()

    def get_token(self, user) -> str:
        return create_token(user.model_dump())

    def verify_password(self, provided_password, stored_password) -> bool:
        return bcrypt.checkpw(provided_password.encode("utf-8"), stored_password)

    def get_username(self, username) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.username == username).first()

    def get_email(self, email) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def get_users(self) -> Optional[UserModel]:
        return self.db.query(UserModel).all()

    def _get_roles(self, role_names: list) -> list[Role]:
        stmt = select(Role).where(Role.name.in_(role_names))
        result = self.db.execute(stmt)
        return result.scalars().all()

    def create_user(self, user: UserModel) -> bool:
        hashed_password = bcrypt.hashpw(user.password.encode("utf-8"), bcrypt.gensalt())
        new_user = UserModel(
            name=user.name if user.name else None,
            surname=user.surname if user.surname else None,
            username=user.username,
            email=user.email,
            password=hashed_password,
        )
        self.db.add(new_user)
        self.db.commit()
        details = "Nuevo usuario"
        self._log_modification(new_user, "create", details)
        return True

    def assign_roles(self, username: str, roles: list) -> bool:
        db_user = self.get_username(username)
        db_roles = self._get_roles(roles)
        db_user.roles = db_roles
        details = "Roles asignados"
        self._log_modification(db_user, "update", details)
        return True

    def update_password(self, username: str, new_pass: str) -> bool:
        db_user = self.get_username(username)
        hashed_password = bcrypt.hashpw(new_pass.encode("utf-8"), bcrypt.gensalt())
        db_user.password = hashed_password
        details = "Password actualizado"
        self._log_modification(db_user, "update", details)
        return True

    def state_user(self, user: UserModel, state: bool) -> bool:
        user.is_active = state
        details = f'El estado actual es {"habilitado" if state else "deshabilitado"}'
        self._log_modification(user, "update", details)
        return True

    def delete_user(self, username: str):
        db_user = self.get_username(username)
        details = f"Usuario eliminado. {jsonable_encoder(db_user)}"
        self._log_modification(db_user, "update", details)
        self.db.delete(db_user)
        self.db.commit()
        return True
