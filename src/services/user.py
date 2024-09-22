from models.user import User as UserModel
from schemas.user import UserCreate

class UserService():
    
    def __init__(self, db) -> None:
        self.db = db

    def create_user(self, user: UserCreate):
        new_user = UserModel(**user.model_dump())
        self.db.add(new_user)
        self.db.commit()
        return new_user.username
