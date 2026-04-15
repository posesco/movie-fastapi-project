from fastapi import APIRouter
from src.api.v1.endpoints import user, movie

api_router = APIRouter()
api_router.include_router(user.router, prefix="/user", tags=["Users"])
api_router.include_router(movie.router, prefix="/movies", tags=["Movies"])
