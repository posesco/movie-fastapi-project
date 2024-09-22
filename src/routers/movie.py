from fastapi import APIRouter
from fastapi import Path, Query, Depends
from fastapi.responses import JSONResponse
from typing import List
from config.database import Session
from models.movie import Movie as MovieModel
from fastapi.encoders import jsonable_encoder
from middlewares.jwt_bearer import JWTBearer
from services.movie import MovieService
from schemas.movie import Movie
movie_router = APIRouter()

@movie_router.get('/movies', tags=['Get movies'], response_model=List[Movie], status_code=200)
def get_movies() -> List[Movie]:
    db = Session()
    result= MovieService(db).get_movies()
    if result:
        return JSONResponse(status_code=200, content=jsonable_encoder(result))
    else:
        return JSONResponse(status_code=404, content={"message" : "No hay peliculas registradas"})

@movie_router.get('/movies/{id}', tags=['Get movies'], response_model=List[Movie], status_code=200)
def get_movie(id: int = Path(ge=1, le=2000)) -> List[Movie]:
    db = Session()
    result= MovieService(db).get_movie(id)
    db.close()
    if result:
        return JSONResponse(status_code=200, content=jsonable_encoder(result))
    else:
        return JSONResponse(status_code=404, content={"message" : "Id de Peli no encontrada"})

@movie_router.get('/movies/', tags=['Get movies'], response_model=List[Movie], status_code=200)
def get_movie_by_category(category: str = Query(min_length=5, max_length=30)) -> List[Movie]:
    db = Session()
    result= MovieService(db).get_movies_by_category(category)
    db.close()
    if result:
        return JSONResponse(status_code=200, content={"message" : f"Se encontraron {len(result)} películas", "Peliculas": jsonable_encoder(result)})
    else:
        return JSONResponse(status_code=404, content={"message" : "Categoria no encontrada"})


@movie_router.post('/movies/', tags=['Modify movies'], response_model=dict, status_code=201, dependencies=[Depends(JWTBearer())])
def create_movies(movies: List[Movie]) -> dict:
    db = Session()
    new_movies = MovieService(db).create_movies(movies)
    db.close()
    return JSONResponse(status_code=201, content={"message": f"Se registraron {len(new_movies)} películas"})

@movie_router.put('/movies/{id}', tags=['Modify movies'], response_model=dict, status_code=200, dependencies=[Depends(JWTBearer())])
def update_movie(id: int, movie: Movie) -> dict:
    db = Session()
    result = MovieService(db).update_movie(id, movie)
    if result:
        db.close()
        return JSONResponse(status_code=200, content={"message" : "Se actualizo la peli"})
    else:
        return JSONResponse(status_code=404, content={"message" : "Id de Peli no encontrada"})

@movie_router.delete('/movies/{id}', tags=['Modify movies'], response_model=dict, status_code=200, dependencies=[Depends(JWTBearer())])
def delete_movie(id: int ) -> dict:
    db = Session()
    result = MovieService(db).delete_movie(id)
    if result:
        db.close()
        return JSONResponse(status_code=200, content={"message" : "Se elimino la peli"})
    else:
        return JSONResponse(status_code=404, content={"message" : "Id de Peli no encontrada"})

