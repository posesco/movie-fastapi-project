from fastapi import APIRouter
from fastapi import Path, Query, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from config.database import Session
from models.movie import Movie as MovieModel
from fastapi.encoders import jsonable_encoder
from middlewares.jwt_bearer import JWTBearer
from datetime import datetime

movie_router = APIRouter()

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

@movie_router.get('/movies', tags=['Get movies'], response_model=List[Movie], status_code=200)
def get_movies() -> List[Movie]:
    db = Session()
    result = db.query(MovieModel).all()
    if result:
        return JSONResponse(status_code=200, content=jsonable_encoder(result))
    else:
        return JSONResponse(status_code=404, content={"message" : "No hay peliculas registradas"})


@movie_router.get('/movies/{id}', tags=['Get movies'], response_model=List[Movie], status_code=200)
def get_movie(id: int = Path(ge=1, le=2000)) -> List[Movie]:
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.id == id).first()
    if result:
        return JSONResponse(status_code=200, content=jsonable_encoder(result))
    else:
        return JSONResponse(status_code=404, content={"message" : "Id de Peli no encontrada"})

@movie_router.get('/movies/', tags=['Get movies'], response_model=List[Movie], status_code=200)
def get_movie_by_category(category: str = Query(min_length=5, max_length=30)) -> List[Movie]:
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.category == category).all()
    if result:
        return JSONResponse(status_code=200, content={"message" : f"Se encontraron {len(result)} películas", "Peliculas": jsonable_encoder(result)})
    else:
        return JSONResponse(status_code=404, content={"message" : "Categoria no encontrada"})


@movie_router.post('/movies/', tags=['Modify movies'], response_model=dict, status_code=201, dependencies=[Depends(JWTBearer())])
def create_movies(movies: List[Movie]) -> dict:
    db = Session()
    new_movies = [MovieModel(**movie.model_dump()) for movie in movies]
    db.add_all(new_movies)
    db.commit()
    db.close()
    return JSONResponse(status_code=201, content={"message": f"Se registraron {len(new_movies)} películas"})

@movie_router.put('/movies/{id}', tags=['Modify movies'], response_model=dict, status_code=200, dependencies=[Depends(JWTBearer())])
def update_movie(id: int, movie: Movie) -> dict:
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.id == id).first()
    if result:
        result.title = movie.title
        result.overview = movie.overview
        result.year = movie.year
        result.rating = movie.rating
        result.category = movie.category
        db.commit()
        db.close()
        return JSONResponse(status_code=200, content={"message" : "Se actualizo la peli"})
    else:
        return JSONResponse(status_code=404, content={"message" : "Id de Peli no encontrada"})

@movie_router.delete('/movies/{id}', tags=['Modify movies'], response_model=dict, status_code=200, dependencies=[Depends(JWTBearer())])
def delete_movie(id: int ) -> dict:
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.id == id).first()
    if result:
        db.delete(result)
        db.commit()
        db.close()
        return JSONResponse(status_code=200, content={"message" : "Se elimino la peli"})
    else:
        return JSONResponse(status_code=404, content={"message" : "Id de Peli no encontrada"})

