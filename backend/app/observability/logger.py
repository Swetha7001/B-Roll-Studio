"""Structured JSON Logging with Correlation & Job Tracking.

Integration Standard Point 8:
Structured JSON logs with timestamp, level, job_id, and X-Correlation-Id.
"""
import contextvars
import json
import logging
import sys
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

# Context variables for request tracing
correlation_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "correlation_id", default=""
)
job_id_ctx: contextvars.ContextVar[str] = contextvars.ContextVar(
    "job_id", default=""
)


class JsonFormatter(logging.Formatter):
    """Custom formatter emitting single-line structured JSON logs."""
    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": correlation_id_ctx.get() or getattr(record, "correlation_id", None),
            "job_id": job_id_ctx.get() or getattr(record, "job_id", None),
        }

        # Include custom extra fields if present
        if hasattr(record, "extra_fields") and isinstance(record.extra_fields, dict):
            log_obj["details"] = record.extra_fields

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


def setup_logging(level: str = "INFO") -> logging.Logger:
    """Configures structured JSON logging on the root handler."""
    root = logging.getLogger()
    root.setLevel(level)

    # Remove existing handlers
    for handler in list(root.handlers):
        root.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)

    # Silence noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    return logging.getLogger("broll_studio")


logger = setup_logging()


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """FastAPI Middleware to manage X-Correlation-Id on all requests and responses."""
    async def dispatch(self, request: Request, call_next) -> Response:
        corr_id = request.headers.get("X-Correlation-Id")
        if not corr_id:
            corr_id = f"corr-{uuid.uuid4().hex[:12]}"
        
        token = correlation_id_ctx.set(corr_id)
        start_time = time.time()

        try:
            response = await call_next(request)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            response.headers["X-Correlation-Id"] = corr_id
            
            # Log incoming request summary
            logger.info(
                f"{request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)",
                extra={"extra_fields": {"duration_ms": duration_ms, "status_code": response.status_code}}
            )
            return response
        finally:
            correlation_id_ctx.reset(token)
