"""B-Roll Studio — FastAPI Main Application Entrypoint.

Implements Sections 7 & 12 (Integration Standard).
All application routes mounted under /api/v1/.
"""
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api.v1.endpoints import broll, storage_view
from app.core.config import settings
from app.core.database import AsyncSessionLocal, init_db
from app.core.errors import AppError, app_exception_handler, generic_exception_handler
from app.observability.logger import CorrelationIdMiddleware, logger
from app.rendering.ffmpeg_engine import ffmpeg_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle handler."""
    logger.info("Initializing B-Roll Studio backend services...")
    await init_db()
    
    # Verify FFmpeg binary availability
    try:
        rc, out, err = await ffmpeg_engine.run_cmd([ffmpeg_engine.ffmpeg_bin, "-version"])
        if rc == 0:
            first_line = out.splitlines()[0] if out.splitlines() else "FFmpeg available"
            logger.info(f"Verified media processor: {first_line}")
        else:
            logger.warning(f"FFmpeg check returned code {rc}: {err}")
    except Exception as e:
        logger.error(f"FFmpeg binary check failed: {e}")

    yield
    logger.info("Shutting down B-Roll Studio backend services.")


app = FastAPI(
    title="IncuBrix B-Roll Studio Engine API",
    description="Automated Script and Voiceover to B-roll Video Generation Engine with Commercial Licensing and Semantic Timing.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# 1. Observability Middlewares
app.add_middleware(CorrelationIdMiddleware)

# 2. CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-Id", "Content-Range", "Accept-Ranges"]
)

# 3. Exception Handlers (Integration Standard Point 5: JSON {"error": {"code", "message", "retryable", "details"}})
app.add_exception_handler(AppError, app_exception_handler)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    error_payload = {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "The request body or parameters failed schema validation.",
            "retryable": False,
            "details": {"errors": exc.errors()}
        }
    }
    return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content=error_payload)


app.add_exception_handler(Exception, generic_exception_handler)

# 4. Mandatory Health & Readiness Endpoints (Integration Standard Point 8)
@app.get("/health", tags=["System"])
async def health_check() -> Dict[str, Any]:
    """Liveness probe returning application metadata."""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.APP_ENV,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/ready", tags=["System"])
async def readiness_check() -> Dict[str, Any]:
    """Readiness probe checking database, storage, and rendering binaries."""
    checks = {}
    is_ready = True

    # 1. Database check
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "healthy"
    except Exception as e:
        checks["database"] = f"unhealthy: {str(e)}"
        is_ready = False

    # 2. FFmpeg binary check
    if Path(ffmpeg_engine.ffmpeg_bin).exists() or ffmpeg_engine.ffmpeg_bin == "ffmpeg":
        checks["ffmpeg"] = "available"
    else:
        checks["ffmpeg"] = "missing"
        is_ready = False

    # 3. Storage directory writable
    try:
        test_file = Path(settings.STORAGE_LOCAL_DIR) / ".health_test"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("ok")
        if test_file.exists():
            test_file.unlink()
        checks["storage"] = "writable"
    except Exception as e:
        checks["storage"] = f"unwritable: {str(e)}"
        is_ready = False

    status_code = status.HTTP_200_OK if is_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ready" if is_ready else "not_ready",
            "checks": checks,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    )


# 5. Mount Core API v1 Routes under /api/v1 (Integration Standard Point 2)
app.include_router(broll.router, prefix=settings.API_V1_PREFIX, tags=["B-Roll Engine"])
app.include_router(storage_view.router, prefix=settings.API_V1_PREFIX, tags=["Storage"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
