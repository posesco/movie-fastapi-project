from fastapi import FastAPI
from fastapi.responses import JSONResponse
from jwt_manager import create_token
from config.database import engine, Base
from middlewares.error_handler import ErrorHandler
from routers.movie import movie_router
from routers.user import user_router

app = FastAPI()
app.title = "Mi aplicación con FastApi"
app.version = "0.0.1"

app.add_middleware(ErrorHandler)
app.include_router(movie_router)
app.include_router(user_router)

Base.metadata.create_all(bind=engine)
   
@app.get('/', tags=['Home'], status_code=200)
async def message():
    return JSONResponse(status_code=200, content={"message": "hello world"})