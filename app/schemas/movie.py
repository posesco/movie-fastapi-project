
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=3, max_length=100)
    overview: str = Field(min_length=15, max_length=350)
    year: int = Field(default_factory=lambda: datetime.now().year)
    rating: float = Field(ge= 1, le=10.0)
    category: str = Field(min_length=3, max_length=30)

    class Config:   
        json_schema_extra = {
            "example" : {
                "title": "Mi Pelicula",
                "overview": "Este es un resumen de la peli",
                "year": 2024,
                "rating": 8.8,
                "category": "Una Categoria X"
            }
        }
