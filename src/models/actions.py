from sqlmodel import Field, SQLModel
import uuid


class Action(SQLModel, table=True):
    __tablename__ = "actions"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=30, unique=True, nullable=False)
