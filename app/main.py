from fastapi import FastAPI, Path, Query, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List
from jwt_manager import create_token, validate_token
from fastapi.security import HTTPBearer
import os
from dotenv import load_dotenv

movies = [
    {
        "id": 1,
        "title": "Avatar",
        "overview": "En un exuberante planeta llamado Pandora viven los Na'vi, seres que...",
        "year": 2009,
        "rating": 7.8,
        "category": "Acción"
    },
    {
        "id": 2,
        "title": "Titanic",
        "overview": "Una tragedia de amor en un barco que se hunde...",
        "year": 1997,
        "rating": 7.8,
        "category": "Drama"
    },
    {
        "id": 3,
        "title": "Gorillaz",
        "overview": "Cualquier cosa puedo ir aca y los Na'vi, seres que...",
        "year": 2021,
        "rating": 9.8,
        "category": "Ficcion"
    }
]
load_dotenv()
ADMIN_EMAIL= os.getenv("ADMIN_EMAIL")
ADMIN_PASS = os.getenv("ADMIN_PASS")
app = FastAPI()
app.title = "Mi aplicación con FastApi"
app.version = "0.0.1"

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
    title: str = Field(min_length=5, max_length=15)
    overview: str = Field(min_length=15, max_length=50)
    year: int = Field(le=2024)
    rating: float = Field(ge= 1, le=10.0)
    category: str = Field(min_length=5, max_length=15)
    
    class Config:
        json_schema_extra = {
            "example" : {
                "id": 1,
                "title": "Mi Pelicula",
                "overview": "Este es un resumen de la peli",
                "year": 2024,
                "rating": 8.8,
                "category": "Una Categoria X"   
            } 
        }


@app.get('/', tags=['home'], status_code=200)
def message():
    return HTMLResponse('<h1>Hello World</h1>')

@app.post('/login', tags=['auth'])
def login(user: User):
    if user.email == ADMIN_EMAIL and user.password == ADMIN_PASS:
        token: str = create_token(user.model_dump())
        return JSONResponse(status_code=200, content=token)

@app.get('/movies', tags=['movies'], response_model=List[Movie], status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies() -> List[Movie]:
    return JSONResponse(status_code=200, content=movies)

@app.get('/movies/{id}', tags=['movies'], response_model=List[Movie], status_code=200)
def get_movie(id: int = Path(ge=1, le=2000)) -> List[Movie]:
    movie = [item for item in movies if item['id'] == id ]
    if movie:
        return JSONResponse(status_code=200, content=movie)
    else:
        return JSONResponse(status_code=404, content={"message" : "Id de Peli no encontrada"})

@app.get('/movies/', tags=['movies'], response_model=List[Movie], status_code=200)
def get_movie_by_category(category: str = Query(min_length=5, max_length=15)) -> List[Movie]:    
    movie = [item for item in movies if item['category'] == category ]
    if movie:
        return JSONResponse(status_code=200, content=movie)
    else:
        return JSONResponse(status_code=404, content={"message" : "Categoria no encontrada"})


@app.post('/movies/', tags=['movies'], response_model=dict, status_code=201)
def create_movie(movie: Movie) -> dict:
    movies.append(movie)
    return JSONResponse(status_code=201, content={"message" : "Se registro la peli"})

@app.put('/movies/{id}', tags=['movies'], response_model=dict, status_code=200)
def update_movie(id: int, movie: Movie) -> dict:
    for item in movies:
        if item['id'] == id:
            item['title'] = movie.title  
            item['overview'] = movie.overview 
            item['year'] = movie.year  
            item['rating'] = movie.rating  
            item['category'] = movie.category
    return JSONResponse(status_code=200, content={"message" : "Se actualizo la peli"})

@app.delete('/movies/{id}', tags=['movies'], response_model=dict, status_code=200)
def delete_movie(id: int ) -> dict:
    movies = [item for item in movies if item['id'] != id]
    return JSONResponse(status_code=200, content={"message" : "Se elimino la peli"})
            
            
