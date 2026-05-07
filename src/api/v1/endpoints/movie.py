from fastapi import Depends, HTTPException, Path, Query, APIRouter, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Annotated

from src.api.deps import SessionDep, CurrentUserDep
from src.services.movie import movie_service
from src.schemas.movie import Movie
from src.models.movie import Movie as MovieModel
from src.models.user import User as UserModel

router = APIRouter(prefix="/movies", tags=["Movies"])

@router.get("/categories", response_model=List[str])
async def get_categories(db: SessionDep) -> List[str]:
    return await movie_service.get_categories(db)

@router.get("/", response_model=List[MovieModel])
async def get_movies(db: SessionDep) -> List[MovieModel]:
    result = await movie_service.get_movies(db)
    return result

@router.get("/{id}", response_model=MovieModel)
async def get_movie(
    db: SessionDep, 
    id: Annotated[int, Path(ge=1, le=2000)]
) -> MovieModel:
    result = await movie_service.get_movie(db, id)
    if not result:
        raise HTTPException(status_code=404, detail="Movie not found")
    return result

@router.get("/category/", response_model=List[MovieModel])
async def get_movie_by_category(
    db: SessionDep,
    category: Annotated[str, Query(min_length=3, max_length=30)],
) -> List[MovieModel]:
    result = await movie_service.get_movies_by_category(db, category)
    return result

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_movie(
    movie: Movie, 
    db: SessionDep,
    current_user: CurrentUserDep
) -> dict:
    model = MovieModel(**movie.model_dump())
    new_movie = await movie_service.create_movie(db, model, current_user)
    return {"success": f"Movie '{new_movie.title}' registered successfully"}

@router.put("/{id}")
async def update_movie(
    id: Annotated[int, Path(ge=1)], 
    movie: Movie, 
    db: SessionDep,
    current_user: CurrentUserDep
) -> dict:
    result = await movie_service.update_movie(db, id, movie.model_dump(), current_user)
    if not result:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"success": "Movie updated"}

@router.delete("/{id}")
async def delete_movie(
    id: Annotated[int, Path(ge=1)], 
    db: SessionDep,
    current_user: CurrentUserDep
) -> dict:
    result = await movie_service.delete_movie(db, id, current_user)
    if not result:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"success": "Movie deleted"}
