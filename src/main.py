from middlewares.error_handler import ErrorHandler
from fastapi.responses import JSONResponse
from config.database import (
    engine, 
    Base,
)
from routers.movie import movie_router
from routers.user import user_router
from fastapi import FastAPI

app = FastAPI(
    title = "Movie API with FastApi",
    version = "0.0.1",
    summary = "This is my initial project with FastAPI, in which I explore and learn about this powerful tool for building modern, high-performance APIs.",
    license_info={
    "name": "GPL-3.0 license",
    "url": "https://www.gnu.org/licenses/gpl-3.0.html",
    },
    terms_of_service="https://posesco.com/terms/",
    contact={
                "name": "Jesus Posada",
                "url": "https://posesco.com/contact/",
                "email": "info@posesco.com",
            },
    debug= True
    
)

@app.get('/', tags=['home'], status_code=200)
async def root():
    return JSONResponse(status_code=200, content={"message": "Hi, Welcome to the movie API"})

@app.get('/healthcheck', tags=['Home'], status_code=200)
async def healthcheck():
    return JSONResponse(status_code=200, content={"message": "The API is LIVE!!"})

app.add_middleware(ErrorHandler)
app.include_router(user_router)
app.include_router(movie_router)

Base.metadata.create_all(bind=engine)
   