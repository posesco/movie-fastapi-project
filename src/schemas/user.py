from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)
from typing import Optional, List, Literal
import uuid
from datetime import datetime


class UserLogin(BaseModel):
    username: str = Field(min_length=5, max_length=30)
    password: str = Field(min_length=5, max_length=30)
    model_config = ConfigDict(extra="forbid")


class UserCreate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=30)
    surname: Optional[str] = Field(default=None, max_length=30)
    username: str = Field(min_length=5, max_length=30)
    email: EmailStr
    password: str = Field(min_length=5, max_length=100)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=200)
    picture: Optional[str] = Field(default=None, max_length=255)

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "name": "John",
                "surname": "Doe",
                "username": "johndoe",
                "email": "johndoe@example.com",
                "password": "password123",
                "phone": "+123456789",
                "address": "123 Main St, New York, NY",
                "picture": "https://example.com/pic.jpg",
            }
        }
    )


class UserRoleAssign(BaseModel):
    username: str
    roles: List[Literal["admin", "editor", "user"]]
    model_config = ConfigDict(extra="forbid")


class UserUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=30)
    surname: Optional[str] = Field(default=None, max_length=30)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=5, max_length=100)
    current_password: Optional[str] = Field(default=None, min_length=5, max_length=30)
    phone: Optional[str] = Field(default=None, max_length=20)
    address: Optional[str] = Field(default=None, max_length=200)
    picture: Optional[str] = Field(default=None, max_length=255)

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "name": "Jane",
                "surname": "Smith",
                "email": "janesmith@example.com",
                "password": "newpassword123",
                "current_password": "oldpassword123",
                "phone": "+987654321",
                "address": "456 Park Ave, London, UK",
                "picture": "https://example.com/newpic.jpg",
            }
        }
    )


class RoleRead(BaseModel):
    id: uuid.UUID
    name: str


class UserRead(BaseModel):
    id: uuid.UUID
    name: Optional[str]
    surname: Optional[str]
    username: str
    email: EmailStr
    phone: Optional[str]
    address: Optional[str]
    picture: Optional[str]
    is_active: bool
    roles: List[RoleRead]
    created_at: datetime


class UserAuditLogRead(BaseModel):
    id: int
    user_id: uuid.UUID
    action_id: uuid.UUID
    action_name: Optional[str] = None
    description: str
    date: datetime

    @classmethod
    def from_orm_with_action(cls, obj):
        return cls(
            id=obj.id,
            user_id=obj.user_id,
            action_id=obj.action_id,
            action_name=obj.action.name if obj.action else None,
            description=obj.description,
            date=obj.date
        )

    model_config = ConfigDict(from_attributes=True)

