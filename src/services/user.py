from models.user import User as UserModel
from schemas.user import UserCreate
import bcrypt

class UserService():
    
    def __init__(self, db) -> None:
        self.db = db

    def create_user(self, user: UserCreate):
        hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
        new_user = UserModel(
                username = user.username,
                email = user.email,
                password = hashed_password
        )
        self.db.add(new_user)
        self.db.commit()
        return new_user
    
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
