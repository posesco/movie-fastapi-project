from models.movie import Movie as MovieModel
from schemas.movie import Movie

class MovieService():
    
    def __init__(self, db) -> None:
        self.db = db
        
    def get_movies(self):
        result = self.db.query(MovieModel).all()
        return result
   
    def get_movie(self, id):
        result = self.db.query(MovieModel).filter(MovieModel.id == id).first()
        return result

    def get_movies_by_category(self, category):
        result = self.db.query(MovieModel).filter(MovieModel.category == category).all()
        return result
    
    def create_movies(self, movies: Movie):
        new_movies = [MovieModel(**movie.model_dump()) for movie in movies]
        self.db.add_all(new_movies)
        self.db.commit()
        return new_movies
    
    def update_movie(self, id, movie: Movie):
        result = self.db.query(MovieModel).filter(MovieModel.id == id).first()
        result.title = movie.title
        result.overview = movie.overview
        result.year = movie.year
        result.rating = movie.rating
        result.category = movie.category
        result.director = movie.director
        result.studio = movie.studio
        result.box_office = movie.box_office
        self.db.commit()
        return result

    def delete_movie(self, id):
        result = self.db.query(MovieModel).filter(MovieModel.id == id).first()
        self.db.delete(result)
        self.db.commit()
        return result
