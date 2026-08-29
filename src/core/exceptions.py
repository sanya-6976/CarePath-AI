import uuid
from typing import Any, Dict, Optional
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from src.core.logging import logger


class DomainException(Exception):
    """Base exception for all domain business errors."""
    def __init__(self, message: str, code: str = "DOMAIN_ERROR", status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class ResourceNotFoundException(DomainException):
    def __init__(self, message: str = "Requested resource not found"):
        super().__init__(message=message, code="RESOURCE_NOT_FOUND", status_code=status.HTTP_404_NOT_FOUND)


class AIServiceUnavailableException(DomainException):
    def __init__(self, message: str = "External AI service is unavailable or timed out"):
        super().__init__(message=message, code="AI_SERVICE_UNAVAILABLE", status_code=status.HTTP_503_SERVICE_UNAVAILABLE)


class InvalidRequestException(DomainException):
    def __init__(self, message: str = "Invalid request payload or parameters"):
        super().__init__(message=message, code="INVALID_REQUEST", status_code=status.HTTP_400_BAD_REQUEST)


class UnauthorizedException(DomainException):
    def __init__(self, message: str = "Authentication required"):
        super().__init__(message=message, code="UNAUTHORIZED", status_code=status.HTTP_401_UNAUTHORIZED)


def create_error_response(code: str, message: str, status_code: int, request_id: Optional[str] = None) -> JSONResponse:
    req_id = request_id or f"req_{uuid.uuid4().hex[:10]}"
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "request_id": req_id,
            }
        }
    )


def setup_exception_handlers(app: FastAPI):
    """Registers global exception handlers enforcing clean, secret-free JSON error structures."""

    @app.exception_handler(DomainException)
    async def domain_exception_handler(request: Request, exc: DomainException):
        logger.warning("domain_exception", code=exc.code, message=exc.message)
        return create_error_response(exc.code, exc.message, exc.status_code)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        code_map = {
            400: "INVALID_REQUEST",
            401: "UNAUTHORIZED",
            403: "FORBIDDEN",
            404: "RESOURCE_NOT_FOUND",
            422: "VALIDATION_ERROR",
            429: "RATE_LIMIT_EXCEEDED",
            500: "INTERNAL_SERVER_ERROR",
            503: "SERVICE_UNAVAILABLE",
        }
        code = code_map.get(exc.status_code, "ERROR")
        msg = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
        return create_error_response(code, msg, exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return create_error_response("VALIDATION_FAILURE", "Invalid request body or parameters", status.HTTP_422_UNPROCESSABLE_ENTITY)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        logger.error("unhandled_internal_error", error=str(exc))
        return create_error_response("INTERNAL_SERVER_ERROR", "An unexpected error occurred", status.HTTP_500_INTERNAL_SERVER_ERROR)
