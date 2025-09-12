from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from rich import print
from rich.panel import Panel

class FastShipError(Exception):
    """Base Exception for all exception is fastship api"""

class EntityNotFound(FastShipError):
    """Exception when entity not found"""
    status_code = status.HTTP_404_NOT_FOUND

class ClientNotAuthorized(FastShipError):
    """Exception when client not authorized"""
    status_code = status.HTTP_401_UNAUTHORIZED

class BadCredentials(FastShipError):
    """Exception when user email or password incorrect"""
    status_code = status.HTTP_401_UNAUTHORIZED

class InvalidToken(FastShipError):
    """Exception when token is invalid or expired"""
    status_code = status.HTTP_401_UNAUTHORIZED

class BadRequest(FastShipError):
    """Exception when bad request"""
    status_code = status.HTTP_400_BAD_REQUEST

class DeliveryPartnerNotAvailable(FastShipError):
    """Exception when delivery partner not available or doesn't have destination"""
    status_code = status.HTTP_400_BAD_REQUEST

class DeliveryPartnerCapacityExceeded(FastShipError):
    """Exception when delivery partner capacity exceeded"""
    status_code = status.HTTP_400_BAD_REQUEST

def _get_handler(status:int, detail:str):
    def handler(request: Request, exception: Exception) -> Response:
        print(Panel(f"Handled: {exception.__class__.__name__}"))
        raise HTTPException(
            status_code=status,
            detail=detail
        )
    return handler

def add_exception_handlers(app: FastAPI):
    for subclass in FastShipError.__subclasses__(): 
        app.add_exception_handler(
            subclass,
            _get_handler(subclass.status_code, subclass.__doc__) # type: ignore
        )

    # for internal server error
    @app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
    def internal_server_error_handler(request: Request, exception: Exception) -> Response:
        print(Panel(f"Handled: {exception}"))
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal Server Error"}
        )

    # for validation error from pydantic
    @app.exception_handler(ResponseValidationError)
    def validation_error_response_handler(request: Request, exception: Exception) -> Response:
        print(Panel(f"Handled: {exception}"))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Validation Error"}
        )

    @app.exception_handler(RequestValidationError)
    def validation_error_request_handler(request: Request, exception: Exception) -> Response:
        print(Panel(f"Handled: {exception}"))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": "Validation Error"}
        )