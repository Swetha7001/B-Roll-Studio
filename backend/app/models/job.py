"""Database models for B-roll jobs, scenes, and artifacts."""
import uuid
from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    idempotency_key = Column(String(128), index=True, nullable=True)
    idempotency_payload_hash = Column(String(64), nullable=True)

    status = Column(String(32), default="queued", index=True, nullable=False)
    progress = Column(Integer, default=0, nullable=False)
    current_stage = Column(String(64), default="queued", nullable=False)

    input_type = Column(String(32), nullable=False)  # "script", "audio", "scenes"
    input_payload = Column(JSON, nullable=False)
    options = Column(JSON, nullable=False)

    callback_url = Column(String(1024), nullable=True)
    callback_secret = Column(String(128), nullable=True)

    # Error fields
    error_code = Column(String(64), nullable=True)
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)
    retryable = Column(Boolean, default=False)

    # Metrics
    cost_estimate = Column(Float, default=0.0)
    processing_duration_sec = Column(Float, default=0.0)

    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    artifacts = relationship("JobArtifact", back_populates="job", cascade="all, delete-orphan")
    scenes = relationship("Scene", back_populates="job", cascade="all, delete-orphan", order_by="Scene.scene_index")


class JobArtifact(Base):
    __tablename__ = "job_artifacts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False, index=True)
    artifact_type = Column(String(64), nullable=False)  # "video_16_9", "video_9_16", "video_1_1", "captions_srt", "timeline_json", "manifest_json"
    file_path = Column(String(1024), nullable=False)
    download_url = Column(String(1024), nullable=False)
    file_size_bytes = Column(Integer, default=0)
    mime_type = Column(String(64), default="application/octet-stream")
    created_at = Column(DateTime(timezone=True), default=utcnow, nullable=False)

    job = relationship("Job", back_populates="artifacts")


class Scene(Base):
    __tablename__ = "scenes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey("jobs.id"), nullable=False, index=True)
    scene_index = Column(Integer, nullable=False)

    narration_text = Column(Text, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    duration = Column(Float, nullable=False)

    visual_intent = Column(Text, nullable=False)
    clip_id = Column(String(128), nullable=False)
    provider = Column(String(64), nullable=False)
    source_url = Column(String(1024), nullable=False)
    download_url = Column(String(1024), nullable=False)

    license_name = Column(String(128), nullable=False)
    license_url = Column(String(1024), nullable=False)
    attribution = Column(Text, nullable=False)
    is_ai_generated = Column(Boolean, default=False, nullable=False)

    selection_reason = Column(Text, nullable=False)
    relevance_score = Column(Float, default=4.0, nullable=False)
    vlm_score = Column(Float, nullable=True)
    human_score = Column(Float, nullable=True)
    fallback_used = Column(Boolean, default=False)
    status = Column(String(32), default="active")

    job = relationship("Job", back_populates="scenes")
