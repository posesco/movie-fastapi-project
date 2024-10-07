import bcrypt
from typing import Optional
from sqlalchemy import select
from fastapi.encoders import jsonable_encoder
from models import User as UserModel, Role
from config.security import create_token, pwd_context, oauth2_scheme
from services.db import DBService
from typing import Annotated
from jwt import decode, ExpiredSignatureError, InvalidTokenError
from fastapi import HTTPException, Depends, status
from config.settings import settings
from schemas.token import TokenData


SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = int(settings.access_token_expire_minutes)


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

    async def get_current_user(self, token: Annotated[str, Depends(oauth2_scheme)]):
        try:
            payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if not username:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="No se han podido validar las credenciales",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            token_data = TokenData(username=username)
        except InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token Invalido",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Token Expirado",
                headers={"WWW-Authenticate": "Bearer"},
            )
        user = self.get_username(token_data.username)
        return user

    async def get_current_active_user(
        self,
        current_user: Annotated[UserModel, Depends(get_current_user)],
    ):
        if not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Usuario deshabilitado"
            )
        return current_user

    def get_token(self, user: dict) -> str:
        return create_token(user)

    def verify_password(self, provided_password, hashed_password) -> bool:
        return pwd_context.verify(provided_password, hashed_password)

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
        hashed_password = pwd_context.hash(user.password)
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
