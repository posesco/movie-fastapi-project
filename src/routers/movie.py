from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi import Path, Query
from sqlalchemy.orm import Session
from typing import List
from config.db import get_db
from fastapi import APIRouter

# from middlewares.jwt_bearer import JWTBearer
from services.movie import MovieService
from schemas.movie import Movie

movie_router = APIRouter()


@movie_router.get(
    "/movies", tags=["Movies"], response_model=List[Movie], status_code=200
)
def get_movies(db: Session = Depends(get_db)) -> List[Movie]:
    result = MovieService(db).get_movies()
    if result:
        return JSONResponse(status_code=200, content=jsonable_encoder(result))
    else:
        raise HTTPException(
            status_code=404, detail={"error": "No hay peliculas registradas"}
        )


@movie_router.get(
    "/movies/{id}", tags=["Movies"], response_model=List[Movie], status_code=200
)
def get_movie(
    db: Session = Depends(get_db), id: int = Path(ge=1, le=2000)
) -> List[Movie]:
    result = MovieService(db).get_movie(id)
    if result:
        return JSONResponse(status_code=200, content=jsonable_encoder(result))
    else:
        raise HTTPException(
            status_code=404, detail={"error": "Id de pelicula no encontrada"}
        )


@movie_router.get(
    "/movies/", tags=["Movies"], response_model=List[Movie], status_code=200
)
def get_movie_by_category(
    db: Session = Depends(get_db),
    category: str = Query(min_length=5, max_length=30),
) -> List[Movie]:
    result = MovieService(db).get_movies_by_category(category)
    if result:
        return JSONResponse(
            status_code=200,
            content={
                "success": f"Se encontraron {len(result)} películas",
                "Películas": jsonable_encoder(result),
            },
        )
    else:
        raise HTTPException(
            status_code=404, detail={"error": "Categoria no encontrada"}
        )


@movie_router.post(
    "/movies/",
    tags=["Movies"],
    response_model=dict,
    status_code=201,
    # dependencies=[Depends(JWTBearer())],
)
def create_movies(movies: List[Movie], db: Session = Depends(get_db)) -> dict:
    new_movies = MovieService(db).create_movies(movies)
    return JSONResponse(
        status_code=201,
        content={"success": f"Se registraron {len(new_movies)} películas"},
    )


@movie_router.put(
    "/movies/{id}",
    tags=["Movies"],
    response_model=dict,
    status_code=200,
    # dependencies=[Depends(JWTBearer())],
)
def update_movie(id: int, movie: Movie, db: Session = Depends(get_db)) -> dict:
    result = MovieService(db).update_movie(id, movie)
    if result:
        return JSONResponse(
            status_code=200, content={"success": "Se actualizo la película"}
        )
    else:
        raise HTTPException(
            status_code=404, detail={"error": "Id de película no encontrada"}
        )


@movie_router.delete(
    "/movies/{id}",
    tags=["Movies"],
    response_model=dict,
    status_code=200,
    # dependencies=[Depends(JWTBearer())],
)
def delete_movie(id: int, db: Session = Depends(get_db)) -> dict:
    result = MovieService(db).delete_movie(id)
    if result:
        return JSONResponse(
            status_code=200, content={"success": "Se elimino la película"}
        )
    else:
        raise HTTPException(
            status_code=404, detail={"error": "Id de película no encontrada"}
        )
