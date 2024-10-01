from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from config.db import (
    engine,
    Base,
)
from middlewares.error_handler import ErrorHandler
from routers.movie import movie_router
from routers.user import user_router
from schemas.health_check import HealthCheck
from services.db import check_db
from models import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Movie API with FastApi",
    version="0.0.1",
    description="""
    This is my initial project with FastAPI, in which I explore and learn
    about this powerful tool for building modern, high-performance APIs.
    """,
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
    debug=False,
    lifespan=lifespan,
)

start_time = datetime.now(timezone.utc)
app.add_middleware(ErrorHandler)
app.include_router(user_router)
app.include_router(movie_router)


@app.get("/", tags=["health"], status_code=301)
async def redirect_to_status():
    return RedirectResponse(url="/_status/")


@app.get("/_status/", response_model=HealthCheck, tags=["health"], status_code=200)
async def health_check():
    db_status = check_db()
    current_time = datetime.now(timezone.utc)
    uptime = current_time - start_time
    return HealthCheck(
        status="OK", version=app.version, db_status=db_status, uptime=str(uptime)
    )


Base.metadata.create_all(bind=engine)
