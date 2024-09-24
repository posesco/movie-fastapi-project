from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator
from typing import Optional

class User(BaseModel):
    username: str = Field(min_length=5, max_length=100) 
    password: str = Field(min_length=5, max_length=100)
    model_config = {"extra":"forbid"}
    
class UserCreate(BaseModel):
    username: str = Field(min_length=5, max_length=100)
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