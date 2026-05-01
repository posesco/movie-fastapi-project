import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Dict, Any

logger = logging.getLogger(__name__)

def get_request_details(request: Request) -> Dict[str, Any]:
    return {
        "method": request.method,
        "url": str(request.url),
        "client": request.client.host if request.client else None,
        "query_params": dict(request.query_params),
    }

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = get_request_details(request)
    logger.error(
        f"Validation Error: {exc.errors()}",
        extra={"request_details": details},
    )
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation Error",
            "type": "RequestValidationError",
            "message": exc.errors(),
            "request": details,
        },
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    details = get_request_details(request)
    logger.error(
        f"HTTP Exception: {exc.status_code} - {exc.detail}",
        extra={"request_details": details},
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": str(exc.detail),
            "type": "HTTPException",
            "request": details,
        },
    )

async def generic_exception_handler(request: Request, exc: Exception):
    details = get_request_details(request)
    logger.error(
        f"Unhandled Exception: {type(exc).__name__} - {str(exc)}",
        extra={"request_details": details},
        exc_info=True,
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "type": type(exc).__name__,
            "message": str(exc),
            "request": details,
        },
    )

def setup_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)
