"""Application Configuration using Pydantic Settings."""
import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server & App metadata
    APP_NAME: str = "B-Roll Studio"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    SECRET_KEY: str = "broll-studio-default-secret-key-change-in-production"
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "*"
    ]

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./broll_studio.db"
    DATABASE_SYNC_URL: str = "sqlite:///./broll_studio.db"

    # Background Tasks
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"
    USE_LOCAL_TASK_RUNNER: bool = True

    # Storage
    STORAGE_BACKEND: str = "local"  # "local" or "s3"
    STORAGE_LOCAL_DIR: str = "./artifacts/storage"
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin"
    MINIO_BUCKET: str = "broll-studio"
    MINIO_SECURE: bool = False

    # Media Binaries
    FFMPEG_PATH: str = "ffmpeg"
    FFPROBE_PATH: str = "ffprobe"

    # AI & Pipeline Adapters
    TTS_PROVIDER: str = "edge"  # "edge" or "mock"
    DEFAULT_VOICE: str = "en-IN-female"
    STT_PROVIDER: str = "whisper_mock"
    FOOTAGE_PRIMARY: str = "curated_stock"
    FOOTAGE_SECONDARY: str = "procedural_gen"
    FOOTAGE_FALLBACK: str = "deterministic_mock"
    RELEVANCE_EVALUATOR: str = "semantic_vlm"

    # Guardrails and Limits
    MAX_AUDIO_DURATION_SEC: int = 600
    MAX_FILE_SIZE_MB: int = 100
    MAX_SCRIPT_CHAR_LENGTH: int = 10000
    DEFAULT_ASPECT_RATIOS: List[str] = ["16:9", "9:16"]
    RENDER_FPS: int = 30
    RENDER_CRF: int = 23
    RENDER_PRESET: str = "fast"

    # Webhooks
    WEBHOOK_TIMEOUT_SEC: int = 10
    WEBHOOK_HMAC_SECRET: str = "incubrix-webhook-secret-key-2026"


# Singleton instance
settings = Settings()
