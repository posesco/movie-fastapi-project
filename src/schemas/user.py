from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from typing import Optional

class User(BaseModel):
    username: Optional[str] = Field(None, min_length=5, max_length=100) 
    email: Optional[EmailStr] = None
    password: str = Field(min_length=5, max_length=100)
    
    @model_validator(mode='before')
    def check_user_or_email(cls, values):
        username = values.get('username')
        email = values.get('email')

        if not username and not email:
            raise ValueError('Debe proporcionar un email o un username.')

        return values

class UserCreate(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(min_length=5, max_length=100)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "usuario",
                "email": "usuario@example.com",
                "password": "password123"
            }
        }
    )