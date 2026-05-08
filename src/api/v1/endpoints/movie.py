from fastapi import Depends, HTTPException, Path, Query, APIRouter, status
from typing import List, Annotated

from src.api.deps import SessionDep, CurrentUserDep, MovieServiceDep
from src.schemas.movie import Movie
from src.models.movie import Movie as MovieModel
from src.schemas.common import ErrorResponse

router = APIRouter(prefix="/movies", tags=["Movies"])

MOVIE_NOT_FOUND = "Movie not found"

@router.get("/categories")
async def get_categories(
    db: SessionDep, 
    movie_service: MovieServiceDep
) -> List[str]:
    return await movie_service.get_categories(db)

@router.get("/")
async def get_movies(
    db: SessionDep, 
    movie_service: MovieServiceDep
) -> List[MovieModel]:
    result = await movie_service.get_movies(db)
    return result

@router.get(
    "/{id}", 
    responses={
        404: {"model": ErrorResponse, "description": MOVIE_NOT_FOUND}
    }
)
async def get_movie(
    db: SessionDep, 
    movie_service: MovieServiceDep,
    id: Annotated[int, Path(ge=1, le=2000)]
) -> MovieModel:
    result = await movie_service.get_movie(db, id)
    if not result:
        raise HTTPException(status_code=404, detail=MOVIE_NOT_FOUND)
    return result

@router.get("/category/")
async def get_movie_by_category(
    db: SessionDep,
    movie_service: MovieServiceDep,
    category: Annotated[str, Query(min_length=3, max_length=30)],
) -> List[MovieModel]:
    result = await movie_service.get_movies_by_category(db, category)
    return result

@router.post(
    "/", 
    status_code=status.HTTP_201_CREATED,
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        400: {"model": ErrorResponse, "description": "Bad Request"}
    }
)
async def create_movie(
    movie: Movie, 
    db: SessionDep,
    movie_service: MovieServiceDep,
    current_user: CurrentUserDep
) -> dict:
    model = MovieModel(**movie.model_dump())
    new_movie = await movie_service.create_movie(db, model, current_user)
    return {"success": f"Movie '{new_movie.title}' registered successfully"}

@router.put(
    "/{id}",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": MOVIE_NOT_FOUND},
        400: {"model": ErrorResponse, "description": "Bad Request"}
    }
)
async def update_movie(
    id: Annotated[int, Path(ge=1)], 
    movie: Movie, 
    db: SessionDep,
    movie_service: MovieServiceDep,
    current_user: CurrentUserDep
) -> dict:
    result = await movie_service.update_movie(db, id, movie.model_dump(), current_user)
    if not result:
        raise HTTPException(status_code=404, detail=MOVIE_NOT_FOUND)
    return {"success": "Movie updated"}

@router.delete(
    "/{id}",
    responses={
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        404: {"model": ErrorResponse, "description": MOVIE_NOT_FOUND},
        400: {"model": ErrorResponse, "description": "Bad Request"}
    }
)
async def delete_movie(
    id: Annotated[int, Path(ge=1)], 
    db: SessionDep,
    movie_service: MovieServiceDep,
    current_user: CurrentUserDep
) -> dict:
    result = await movie_service.delete_movie(db, id, current_user)
    if not result:
        raise HTTPException(status_code=404, detail=MOVIE_NOT_FOUND)
    return {"success": "Movie deleted"}
