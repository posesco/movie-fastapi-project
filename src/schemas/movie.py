from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
)
from datetime import datetime, timezone
from typing import Optional


class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=3, max_length=100)
    overview: str = Field(min_length=15, max_length=350)
    year: int = Field(default_factory=lambda: datetime.now(timezone.utc).year)
    rating: float = Field(ge=1, le=10.0)
    category: str = Field(min_length=3, max_length=30)
    director: str = Field(min_length=3, max_length=30)
    studio: str = Field(min_length=3, max_length=60)
    box_office: int = Field(default_factory=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "title": "Mi Pelicula",
                "overview": "Este es un resumen de la peli",
                "year": 2024,
                "rating": 8.8,
                "category": "Una Categoria X:X",
                "director": "Director X",
                "studio": "Studio X",
                "box_office": 1046132472,
            }
        }
    )
