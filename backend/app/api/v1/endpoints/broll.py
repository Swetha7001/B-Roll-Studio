"""B-Roll Studio API Endpoints.

Implements Sections 7 & 11 and Integration Standard Points 2, 3, 4, 5, 7.
"""
import asyncio
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, Header, Query, Request, Response, UploadFile, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.errors import (
    AppError, EmptyScriptError, IdempotencyConflictError, InvalidAudioError, NotFoundError,
    UnsupportedMediaTypeError, ValidationError
)
from app.models.job import Job, JobArtifact, Scene
from app.observability.logger import logger
from app.rendering.partial_renderer import partial_renderer
from app.schemas.job import (
    JobCreateRequest, JobResultLinks, JobResultResponse, JobStatusResponse, SceneInputItem, SceneSwapRequest
)
from app.storage.storage_manager import storage
from app.workers.job_runner import job_runner

router = APIRouter()


def compute_payload_hash(payload_dict: dict) -> str:
    """Computes deterministic SHA-256 hash of canonical JSON payload."""
    canonical_str = json.dumps(payload_dict, sort_keys=True)
    return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()


@router.post(
    "/broll/jobs",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=JobStatusResponse,
    summary="Create a new B-roll video generation job"
)
async def create_broll_job(
    request: Request,
    background_tasks: BackgroundTasks,
    payload: Optional[JobCreateRequest] = None,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db)
):
    """
    Submits a video creation job from script, audio URL, or structured scenes.
    Safe Retries: If Idempotency-Key is provided, repeated requests return the same job.
    """
    if payload is None:
        raise ValidationError("Request body is required.")

    payload_dict = payload.model_dump(exclude_none=True)
    payload_hash = compute_payload_hash(payload_dict)

    # 1. Idempotency Key Handling (Integration Standard Point 4)
    if idempotency_key:
        stmt = select(Job).where(Job.idempotency_key == idempotency_key)
        res = await db.execute(stmt)
        existing_job = res.scalar_one_or_none()

        if existing_job:
            if existing_job.idempotency_payload_hash != payload_hash:
                raise IdempotencyConflictError(
                    f"Idempotency-Key '{idempotency_key}' was previously used with a different request payload."
                )
            logger.info(f"Idempotent hit for key '{idempotency_key}'. Returning existing Job {existing_job.id}")
            return await build_job_status_response(existing_job, db)

    # 2. Input determination
    if payload.audio_url:
        input_type = "audio"
        input_data = {"audio_url": payload.audio_url}
    elif payload.scenes:
        input_type = "scenes"
        input_data = {"scenes": [s.model_dump() for s in payload.scenes]}
    elif payload.script:
        if not payload.script.strip():
            raise EmptyScriptError("Script cannot be empty or purely whitespace.")
        input_type = "script"
        input_data = {"script": payload.script}
    else:
        raise ValidationError("One of 'audio_url', 'script', or 'scenes' must be supplied.")

    # 3. Create Job Record
    job_id = str(uuid.uuid4())
    options = {
        "voice": payload.voice or settings.DEFAULT_VOICE,
        "aspect_ratios": payload.aspect_ratios,
        "style": payload.style,
        "avoid": payload.avoid,
        "captions": payload.captions.model_dump(),
    }

    new_job = Job(
        id=job_id,
        idempotency_key=idempotency_key,
        idempotency_payload_hash=payload_hash,
        status="queued",
        progress=0,
        current_stage="queued",
        input_type=input_type,
        input_payload=input_data,
        options=options,
        callback_url=payload.callback_url
    )

    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    # 4. Dispatch Asynchronous Background Job (Integration Standard Point 3)
    background_tasks.add_task(job_runner.run_job, job_id)

    logger.info(f"Job {job_id} queued successfully via API.")
    return await build_job_status_response(new_job, db)


@router.post(
    "/broll/jobs/upload",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=JobStatusResponse,
    summary="Create a new B-roll video job with direct audio file upload"
)
async def upload_audio_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    voice: Optional[str] = Form("en-IN-female"),
    aspect_ratios: Optional[str] = Form('["16:9","9:16"]'),
    style: Optional[str] = Form("bright, modern, real-world footage"),
    avoid: Optional[str] = Form("[]"),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db)
):
    """Multipart upload endpoint supporting direct MP3, WAV, and M4A audio files."""
    filename = file.filename or "uploaded_audio.wav"
    ext = Path(filename).suffix.lower()
    if ext not in (".mp3", ".wav", ".m4a", ".ogg"):
        raise UnsupportedMediaTypeError(f"Unsupported audio format '{ext}'. Must be mp3, wav, or m4a.")

    job_id = str(uuid.uuid4())
    stored_path = f"{job_id}/input_audio{ext}"
    
    # Store uploaded audio in storage
    storage_url = storage.put_file(stored_path, file.file, content_type=file.content_type or "audio/wav")

    try:
        ratios = json.loads(aspect_ratios) if aspect_ratios else ["16:9", "9:16"]
        avoid_list = json.loads(avoid) if avoid else []
    except Exception:
        ratios = ["16:9", "9:16"]
        avoid_list = []

    options = {
        "voice": voice,
        "aspect_ratios": ratios,
        "style": style,
        "avoid": avoid_list,
        "captions": {"burn_in": True, "srt": True}
    }

    new_job = Job(
        id=job_id,
        idempotency_key=idempotency_key,
        idempotency_payload_hash=f"file-upload-{job_id}",
        status="queued",
        progress=0,
        current_stage="queued",
        input_type="audio",
        input_payload={"audio_url": f"local://{stored_path}"},
        options=options
    )

    db.add(new_job)
    await db.commit()
    await db.refresh(new_job)

    background_tasks.add_task(job_runner.run_job, job_id)
    return await build_job_status_response(new_job, db)


@router.get(
    "/jobs/{job_id}",
    response_model=JobStatusResponse,
    summary="Check job processing status and progress"
)
@router.get(
    "/broll/jobs/{job_id}",
    response_model=JobStatusResponse,
    include_in_schema=False
)
async def get_job_status(job_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves current job status, 0-100 progress percentage, and artifacts when ready."""
    stmt = select(Job).where(Job.id == job_id)
    res = await db.execute(stmt)
    job = res.scalar_one_or_none()

    if not job:
        raise NotFoundError(f"Job with ID '{job_id}' not found.", code="JOB_NOT_FOUND")

    return await build_job_status_response(job, db)


@router.get(
    "/broll/jobs/{job_id}/result",
    response_model=JobResultResponse,
    summary="Retrieve completed job output artifacts, timeline and manifest"
)
async def get_job_result(job_id: str, db: AsyncSession = Depends(get_db)):
    """Retrieves all generated video links, captions, manifest.json, and timeline.json."""
    stmt = select(Job).where(Job.id == job_id)
    res = await db.execute(stmt)
    job = res.scalar_one_or_none()

    if not job:
        raise NotFoundError(f"Job with ID '{job_id}' not found.", code="JOB_NOT_FOUND")

    if job.status != "succeeded":
        raise AppError(
            code="JOB_NOT_READY",
            message=f"Job is in '{job.status}' state. Results only available when succeeded.",
            status_code=400
        )

    # Collect artifacts
    art_stmt = select(JobArtifact).where(JobArtifact.job_id == job_id)
    art_res = await db.execute(art_stmt)
    artifacts = {a.artifact_type: a.download_url for a in art_res.scalars().all()}

    # Read manifest and timeline if available locally
    job_dir = Path(settings.STORAGE_LOCAL_DIR).resolve() / job_id
    manifest_data = None
    timeline_data = None

    if (job_dir / "manifest.json").exists():
        with open(job_dir / "manifest.json", "r", encoding="utf-8") as f:
            manifest_data = json.load(f)

    if (job_dir / "timeline.json").exists():
        with open(job_dir / "timeline.json", "r", encoding="utf-8") as f:
            timeline_data = json.load(f)

    aspect_ratios = job.options.get("aspect_ratios", ["16:9"])

    return JobResultResponse(
        job_id=job.id,
        status=job.status,
        aspect_ratios=aspect_ratios,
        artifacts=artifacts,
        manifest=manifest_data,
        timeline=timeline_data,
        cost_estimate_usd=job.cost_estimate or 0.0,
        processing_duration_sec=job.processing_duration_sec or 0.0
    )


@router.post(
    "/broll/jobs/{job_id}/scenes/{scene_index}/swap",
    summary="Swap a scene clip and perform partial re-render (Advanced Requirement ADV-2)"
)
async def swap_scene_clip(
    job_id: str,
    scene_index: int,
    request: SceneSwapRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Replaces one scene's clip and triggers accelerated partial re-render,
    re-rendering ONLY the affected portion in clearly less time than a full render.
    """
    stmt = select(Job).where(Job.id == job_id)
    res = await db.execute(stmt)
    job = res.scalar_one_or_none()
    if not job:
        raise NotFoundError(f"Job '{job_id}' not found.")

    job_dir = Path(settings.STORAGE_LOCAL_DIR).resolve() / job_id
    timeline_file = job_dir / "timeline.json"
    if not timeline_file.exists():
        raise NotFoundError("Timeline for job not found.")

    with open(timeline_file, "r", encoding="utf-8") as f:
        timeline_data = json.load(f)

    scenes_list = timeline_data.get("scenes", [])
    if scene_index < 0 or scene_index >= len(scenes_list):
        raise ValidationError(f"Scene index {scene_index} is out of bounds (total scenes: {len(scenes_list)}).")

    # Resolve replacement clip
    from app.adapters.footage.stock_provider import CuratedStockProvider
    stock_prov = CuratedStockProvider()
    replacement_clip = None

    if request.new_clip_id:
        replacement_clip = await stock_prov.get_clip_by_id(request.new_clip_id)

    if not replacement_clip:
        # Search candidate matching new_visual_hint or fallback
        hint = request.new_visual_hint or "creative modern workplace"
        candidates = await stock_prov.search(hint, hint, 6.0)
        replacement_clip = candidates[0]

    # Reconstruct planned scenes
    from app.services.scene_planner import PlannedScene
    from app.services.footage_selector import SelectedClipRecord

    planned_scenes = []
    selected_clips = []
    for s in scenes_list:
        sc = PlannedScene(
            scene_index=s["scene_index"],
            narration_text=s["narration_text"],
            start_time=s["start_time"],
            end_time=s["end_time"],
            duration=s["duration"],
            visual_intent=s["visual_intent"],
            category=s.get("category", "general"),
            suggested_palette="cyan",
            safety_notes=[],
            avoid_tags=[]
        )
        planned_scenes.append(sc)

        clip_info = s["selected_clip"]
        from app.adapters.footage.base import FootageClip
        clip_obj = FootageClip(
            clip_id=clip_info["clip_id"],
            provider=clip_info["provider"],
            title=clip_info["title"],
            description="",
            duration=s["duration"],
            width=1920,
            height=1080,
            aspect_ratio="16:9",
            source_url=clip_info["source_url"],
            download_url=clip_info["download_url"],
            license_name=clip_info["license_name"],
            license_url=clip_info["license_url"],
            attribution=clip_info["attribution"],
            is_ai_generated=clip_info["is_ai_generated"],
        )
        selected_clips.append(SelectedClipRecord(
            scene_index=s["scene_index"],
            clip=clip_obj,
            provider_chosen=clip_obj.provider,
            selection_reason=s["selection_decision"]["selection_reason"],
            relevance_score=s["selection_decision"]["relevance_score"],
            vlm_score=s["selection_decision"]["vlm_score"],
            human_rating_estimate=s["selection_decision"]["human_rating_estimate"],
            fallback_used=s["selection_decision"]["fallback_used"]
        ))

    aspect_ratios = job.options.get("aspect_ratios", ["16:9"])
    narration_wav = job_dir / "narration.wav"
    captions_srt = job_dir / "captions.srt"

    # Execute Partial Re-render
    artifacts_map, partial_dur, full_dur_est = await partial_renderer.swap_and_re_render(
        job_dir=job_dir,
        job_id=job_id,
        scene_index=scene_index,
        new_clip=replacement_clip,
        planned_scenes=planned_scenes,
        selected_clips=selected_clips,
        aspect_ratios=aspect_ratios,
        narration_wav=narration_wav,
        captions_srt=captions_srt if captions_srt.exists() else None,
        burn_in_captions=job.options.get("captions", {}).get("burn_in", True)
    )

    return {
        "status": "success",
        "job_id": job_id,
        "scene_index": scene_index,
        "swapped_clip": replacement_clip.to_dict(),
        "partial_render_duration_sec": partial_dur,
        "full_render_estimate_sec": full_dur_est,
        "speedup_factor": round(full_dur_est / max(0.1, partial_dur), 1),
        "artifacts": artifacts_map
    }


@router.get(
    "/jobs",
    summary="List all jobs with optional status filter and pagination"
)
async def list_jobs(
    status_filter: Optional[str] = Query(None, alias="status"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Returns paginated list of recent jobs for the dashboard workspace."""
    stmt = select(Job).order_by(desc(Job.created_at))
    if status_filter:
        stmt = stmt.where(Job.status == status_filter)
    
    stmt = stmt.offset(offset).limit(limit)
    res = await db.execute(stmt)
    jobs = res.scalars().all()

    items = []
    for j in jobs:
        items.append(await build_job_status_response(j, db))
    return {"total": len(items), "jobs": items}


async def build_job_status_response(job: Job, db: AsyncSession) -> JobStatusResponse:
    """Helper to assemble JobStatusResponse."""
    results_links = None
    if job.status == "succeeded":
        art_stmt = select(JobArtifact).where(JobArtifact.job_id == job.id)
        art_res = await db.execute(art_stmt)
        arts = {a.artifact_type: a.download_url for a in art_res.scalars().all()}
        results_links = JobResultLinks(
            video_16_9=arts.get("video_16_9"),
            video_9_16=arts.get("video_9_16"),
            video_1_1=arts.get("video_1_1"),
            captions_srt=arts.get("captions_srt"),
            timeline_json=arts.get("timeline_json"),
            manifest_json=arts.get("manifest_json"),
            audio_narration=arts.get("audio_narration")
        )

    error_info = None
    if job.status == "failed" and job.error_code:
        error_info = {
            "code": job.error_code,
            "message": job.error_message or "Job processing encountered an error.",
            "retryable": job.retryable,
            "details": job.error_details or {}
        }

    return JobStatusResponse(
        job_id=job.id,
        status=job.status,
        progress=job.progress,
        current_stage=job.current_stage,
        created_at=job.created_at,
        updated_at=job.updated_at,
        result=results_links,
        error=error_info
    )
