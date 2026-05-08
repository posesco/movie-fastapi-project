from fastapi import FastAPI, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from datetime import datetime, timezone
from contextlib import asynccontextmanager
import socket

from .core.database import init_db
from .core.redis import init_redis, close_redis
from .core.config import settings, tags_metadata
from .core.observability import setup_observability
from .middlewares.handlers import setup_exception_handlers

from .api.v1.router import api_router
from fastapi.staticfiles import StaticFiles


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_redis()
    yield
    await close_redis()


app = FastAPI(
    title=settings.project_title,
    version=settings.project_version,
    description=settings.project_desc,
    debug=settings.project_debug_mode,
    lifespan=lifespan,
    openapi_tags=tags_metadata,
)

# Setup CORS
if settings.backend_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin).rstrip("/") for origin in settings.backend_cors_origins],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Trusted Hosts
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=settings.allowed_hosts
)

# Setup Observability
setup_observability(app)

# Setup Exception Handlers
setup_exception_handlers(app)

# Mount local storage if enabled (OCP)
if settings.storage_backend == "local":
    import os
    os.makedirs(settings.local_storage_path, exist_ok=True)
    app.mount("/static", StaticFiles(directory=settings.local_storage_path), name="static")

app.include_router(api_router, prefix="/api/v1")

start_time = datetime.now(timezone.utc)


@app.get("/", tags=["health"], status_code=status.HTTP_302_FOUND)
async def redirect_to_status() -> RedirectResponse:
    return RedirectResponse(url="/_status/", status_code=status.HTTP_302_FOUND)


@app.get("/_status/", tags=["health"], status_code=200)
async def _status() -> dict:
    from sqlmodel import select
    from .core.database import engine

    db_status = "OK"
    api_status = "Live"
    try:
        async with engine.connect() as conn:
            await conn.execute(select(1))
    except Exception as e:
        db_status = f"Error: {str(e)}"
        api_status = "Dead"

    current_time = datetime.now(timezone.utc)
    uptime = current_time - start_time
    return JSONResponse(
        status_code=200,
        content={
            "status": api_status,
            "version": app.version,
            "db_status": db_status,
            "uptime": str(uptime),
            "server": socket.gethostbyaddr(socket.gethostname()),
        },
    )


@app.get("/health-check/", tags=["health"], status_code=200)
async def health_check() -> bool:
    return True
