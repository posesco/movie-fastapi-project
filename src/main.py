from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse, JSONResponse
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from config.db import engine, Base
from config.settings import settings, tags_metadata
from middlewares.error_handler import ErrorHandler
from routers.movie import movie_router
from routers.user import user_router
from services.db import DBService
from models import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.project_title,
    version=settings.project_version,
    description=settings.project_desc,
    debug=settings.project_debug_mode,
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)

start_time = datetime.now(timezone.utc)
app.add_middleware(ErrorHandler)
app.include_router(user_router)
app.include_router(movie_router)


@app.get("/", tags=["health"], status_code=status.HTTP_302_FOUND)
async def redirect_to_status() -> RedirectResponse:
    return RedirectResponse(url="/_status/", status_code=status.HTTP_302_FOUND)


@app.get("/_status/", tags=["health"], status_code=200)
async def health_check() -> dict:
    db_status = DBService().check_db()
    current_time = datetime.now(timezone.utc)
    uptime = current_time - start_time
    return JSONResponse(
        status_code=200,
        content={
            "status": "Live",
            "version": app.version,
            "db_status": db_status,
            "uptime": str(uptime),
        },
    )


Base.metadata.create_all(bind=engine)
