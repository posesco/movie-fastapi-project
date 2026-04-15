from src.models.movie import Movie
from .base import BaseRepository

class MovieRepository(BaseRepository[Movie]):
    """Movie-specific repository."""
    pass

movie_repository = MovieRepository(Movie)
