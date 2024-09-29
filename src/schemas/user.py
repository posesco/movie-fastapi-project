from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)
from typing import Optional


class UserLogin(BaseModel):
    username: str = Field(min_length=5, max_length=30)
    password: str = Field(min_length=5, max_length=30)
    model_config = {"extra": "forbid"}


class UserCreate(BaseModel):
    name: Optional[str] = Field(min_length=3, max_length=30)
    surname: Optional[str] = Field(min_length=3, max_length=30)
    username: str = Field(min_length=5, max_length=30)
    email: EmailStr
    password: str = Field(min_length=5, max_length=100)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "Manuel",
                "surname": "Turizo",
                "username": "manutur",
                "email": "joe@doe.com",
                "password": "password123",
            }
        }
    )
