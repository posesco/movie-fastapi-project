import traceback
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse

class ErrorHandler(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next) -> Response | JSONResponse:
        try:
            return await call_next(request)
        except Exception as e:
            error_traceback = traceback.format_exc()
            request_details = {
                "method": request.method,
                "url": request.url.path,
                "headers": dict(request.headers)
            }
            error_response = {
                "error": str(e),  
                "type": type(e).__name__,  
                "traceback": error_traceback,  
                "request": request_details
            }
            return JSONResponse(status_code=500, content=error_response)
        
