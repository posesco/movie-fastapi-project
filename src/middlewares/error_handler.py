from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from typing import Dict, Any
import logging


class ErrorHandler(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)
        self.logger = logging.getLogger(__name__)

    async def dispatch(self, request: Request, call_next) -> Response | JSONResponse:
        try:
            return await call_next(request)
        except Exception as exc:
            return await self.handle_exception(request, exc)

    async def handle_exception(self, request: Request, exc: Exception) -> JSONResponse:
        request_details = self.get_request_details(request)
        error_response = self.format_error_response(exc, request_details)

        self.log_error(exc, request_details)

        return JSONResponse(
            status_code=self.get_status_code(exc), content=error_response
        )

    def get_request_details(self, request: Request) -> Dict[str, Any]:
        return {
            "method": request.method,
            "url": str(request.url),
            "headers": dict(request.headers),
            "client": request.client.host if request.client else None,
            "query_params": dict(request.query_params),
        }

    def format_error_response(
        self, exc: Exception, request_details: Dict[str, Any]
    ) -> Dict[str, Any]:
        return {
            "error": str(exc),
            "type": type(exc).__name__,
            "request": request_details,
        }

    def log_error(self, exc: Exception, request_details: Dict[str, Any]) -> None:
        self.logger.error(
            f"Exception occurred: {type(exc).__name__} - {str(exc)}",
            extra={"request_details": request_details},
            exc_info=True,
        )

    def get_status_code(self, exc: Exception) -> int:
        if hasattr(exc, "status_code"):
            return exc.status_code
        return 500
