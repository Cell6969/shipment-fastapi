from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.worker.tasks import add_log


def set_middlware(app:FastAPI):
    # setup cors
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # add custom middleware
    class LoggingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request:Request, call_next):
            method = request.method
            url = request.url.path
            client = request.client
            add_log.delay(f"{method} {url} {client}")
            response = await call_next(request)
            return response

    class PublicMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request:Request, call_next):
            if request.url.path == "/shipment/":
                x_token = request.headers.get("X-Token")
                if not x_token:
                    return JSONResponse(status_code=401, content={"detail": "X-Token not found"})
                response = await call_next(request)
                return response
            return await call_next(request)

    
    app.add_middleware(LoggingMiddleware)
    # app.add_middleware(PublicMiddleware)