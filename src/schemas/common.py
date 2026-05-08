from pydantic import BaseModel
from typing import List

class PaginatedResponse[T](BaseModel):
    items: List[T]
    total: int
    skip: int
    limit: int

class ErrorResponse(BaseModel):
    error: str
