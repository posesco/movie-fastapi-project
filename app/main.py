from fastapi import FastAPI, Path, Query, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from jwt_manager import create_token, validate_token
from fastapi.security import HTTPBearer
import os
from dotenv import load_dotenv
from config.database import Session, engine, Base
from models.movie import Movie as MovieModel
from fastapi.encoders import jsonable_encoder

load_dotenv()
ADMIN_EMAIL= os.getenv("ADMIN_EMAIL")
ADMIN_PASS = os.getenv("ADMIN_PASS")

app = FastAPI()
app.title = "Mi aplicación con FastApi"
app.version = "0.0.1"

Base.metadata.create_all(bind=engine)

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        auth = await super().__call__(request)
        data = validate_token(auth.credentials)
        if data['email'] != ADMIN_EMAIL:
            raise HTTPException(status_code=403, detail="Credenciales invalidas")
        
class User(BaseModel):
    email: str
    password: str
    
class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=5, max_length=100)
    overview: str = Field(min_length=15, max_length=350)
    year: int = Field(le=2024)
    rating: float = Field(ge= 1, le=10.0)
    category: str = Field(min_length=5, max_length=30)

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

@app.get('/', tags=['home'], status_code=200)
async def message():
    return JSONResponse(status_code=200, content={"message": "hello world"})

@app.post('/login', tags=['auth'])
def login(user: User):
    if user.email == ADMIN_EMAIL and user.password == ADMIN_PASS:
        token: str = create_token(user.model_dump())
        return JSONResponse(status_code=200, content=token)

@app.get('/movies', tags=['movies'], response_model=List[Movie], status_code=200)
def get_movies() -> List[Movie]:
    db = Session()
    result = db.query(MovieModel).all()
    if result:
        return JSONResponse(status_code=200, content=jsonable_encoder(result))
    else:
        return JSONResponse(status_code=404, content={"message" : "No hay peliculas registradas"})


@app.get('/movies/{id}', tags=['movies'], response_model=List[Movie], status_code=200)
def get_movie(id: int = Path(ge=1, le=2000)) -> List[Movie]:
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.id == id).first()
    if result:
        return JSONResponse(status_code=200, content=jsonable_encoder(result))
    else:
        return JSONResponse(status_code=404, content={"message" : "Id de Peli no encontrada"})

@app.get('/movies/', tags=['movies'], response_model=List[Movie], status_code=200)
def get_movie_by_category(category: str = Query(min_length=5, max_length=30)) -> List[Movie]:
    db = Session()
    result = db.query(MovieModel).filter(MovieModel.category == category).all()
    if result:
        return JSONResponse(status_code=200, content={"message" : f"Se encontraron {len(result)} películas", "Peliculas": jsonable_encoder(result)})
    else:
        return JSONResponse(status_code=404, content={"message" : "Categoria no encontrada"})


@app.post('/movies/', tags=['movies'], response_model=dict, status_code=201, dependencies=[Depends(JWTBearer())])
def create_movies(movies: List[Movie]) -> dict:
    db = Session()
    new_movies = [MovieModel(**movie.model_dump()) for movie in movies]
    db.add_all(new_movies)
    db.commit()
    db.close()
    return JSONResponse(status_code=201, content={"message": f"Se registraron {len(new_movies)} películas"})

@app.put('/movies/{id}', tags=['movies'], response_model=dict, status_code=200, dependencies=[Depends(JWTBearer())])
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

@app.delete('/movies/{id}', tags=['movies'], response_model=dict, status_code=200, dependencies=[Depends(JWTBearer())])
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

