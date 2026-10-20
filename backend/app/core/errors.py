"""Standardised Error Handling and Exceptions.

Integration Standard Point 5:
Errors are JSON: {"error": {"code", "message", "retryable", "details"}}
Codes are UPPER_SNAKE_CASE.
"""
from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppError(Exception):
    """Base application exception."""
    def __init__(
        self,
        code: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        retryable: bool = False,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.retryable = retryable
        self.details = details or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "retryable": self.retryable,
                "details": self.details,
            }
        }


# Concrete typed exceptions
class ValidationError(AppError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="VALIDATION_ERROR",
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            retryable=False,
            details=details,
        )


class UnsupportedMediaTypeError(AppError):
    def __init__(self, message: str = "Unsupported media format. Supported formats: mp3, wav, m4a"):
        super().__init__(
            code="UNSUPPORTED_MEDIA_TYPE",
            message=message,
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            retryable=False,
        )


class InvalidAudioError(AppError):
    def __init__(self, message: str, code: str = "INVALID_AUDIO_FORMAT", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            retryable=False,
            details=details,
        )


class SilentAudioError(AppError):
    def __init__(self, message: str = "Uploaded audio contains only silence or undetectable speech"):
        super().__init__(
            code="SILENT_AUDIO_DETECTED",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            retryable=False,
        )


class EmptyScriptError(AppError):
    def __init__(self, message: str = "Script cannot be empty or purely whitespace"):
        super().__init__(
            code="EMPTY_SCRIPT_ERROR",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            retryable=False,
        )


class IdempotencyConflictError(AppError):
    def __init__(self, message: str = "Idempotency key reused with different request payload"):
        super().__init__(
            code="IDEMPOTENCY_CONFLICT",
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            retryable=False,
        )


class NotFoundError(AppError):
    def __init__(self, message: str, code: str = "NOT_FOUND"):
        super().__init__(
            code=code,
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            retryable=False,
        )


class FootageProviderError(AppError):
    def __init__(self, message: str, retryable: bool = True, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="FOOTAGE_PROVIDER_ERROR",
            message=message,
            status_code=status.HTTP_502_BAD_GATEWAY,
            retryable=retryable,
            details=details,
        )


class RenderError(AppError):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            code="RENDER_ERROR",
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            retryable=True,
            details=details,
        )


class SsrfBlockedError(AppError):
    def __init__(self, message: str = "Target URL is blocked by SSRF protection policy"):
        super().__init__(
            code="SSRF_ATTEMPT_BLOCKED",
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            retryable=False,
        )


async def app_exception_handler(request: Request, exc: AppError) -> JSONResponse:
    """FastAPI exception handler for AppError instances."""
    return JSONResponse(status_code=exc.status_code, content=exc.to_dict())


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """FastAPI fallback handler for unhandled exceptions (never leaking internal stack trace)."""
    error_payload = {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected internal server error occurred. Please retry later.",
            "retryable": True,
            "details": {"type": exc.__class__.__name__}
        }
    }
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_payload
    )
