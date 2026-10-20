"""Google AI Video Generation Center Endpoints.

Provides direct access to Gemini Pro Script Director and Google Veo
Animated Video Generation with timestamped scenes.
"""
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from pydantic import BaseModel, Field

from app.adapters.google_ai.gemini_director import StoryboardResult, gemini_director
from app.adapters.google_ai.veo_video_engine import google_veo_engine
from app.observability.logger import logger
from app.storage.storage_manager import storage

router = APIRouter()

# In-memory job state store for Google Studio jobs
GOOGLE_JOBS: Dict[str, Dict[str, Any]] = {}


class StoryboardRequest(BaseModel):
    script: str = Field(..., min_length=5, description="User story prompt or text script")
    animation_style: str = Field("3d_animation", description="Style: 3d_animation, anime, hyper_realistic, cyberpunk")
    api_key: Optional[str] = Field(None, description="Optional Google AI Studio Gemini API Key")


class GenerateVideoRequest(BaseModel):
    storyboard: StoryboardResult
    voice: str = Field("en-IN-female", description="Narration voice")
    aspect_ratio: str = Field("16:9", description="Aspect ratio (16:9, 9:16, 1:1)")
    burn_captions: bool = Field(True, description="Burn in subtitles")
    api_key: Optional[str] = Field(None, description="Google AI Studio Gemini API Key")


class ApiKeyConfigRequest(BaseModel):
    api_key: str = Field(..., description="Google Gemini API Key")


@router.get("/config")
async def get_google_config():
    """Returns Google AI Studio integration status."""
    return {
        "gemini_pro_ready": True,
        "configured_with_user_key": gemini_director.is_configured(),
        "supported_models": ["gemini-2.0-flash", "gemini-1.5-pro", "google-veo-2.0"],
        "supported_styles": [
            {"id": "3d_animation", "label": "🎬 3D Pixar / Disney Animation", "description": "Expressive 3D animated characters with soft volumetric lighting"},
            {"id": "anime", "label": "🌟 Cinematic Anime (Studio Ghibli)", "description": "Hand-crafted anime aesthetic with vibrant skies and emotional detail"},
            {"id": "hyper_realistic", "label": "🎥 Hyper-Realistic Motion (Veo Cinema)", "description": "Full-motion 8K cinematic lens quality with anamorphic bokeh"},
            {"id": "cyberpunk", "label": "⚡ Cyberpunk Neon Motion", "description": "Futuristic neon atmosphere with glowing particle effects"}
        ]
    }


@router.post("/config")
async def save_google_api_key(req: ApiKeyConfigRequest):
    """Validates and sets the Google Gemini API key."""
    key = req.api_key.strip()
    if not (key.startswith("AQ.") or key.startswith("AIza") or len(key) >= 16):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Google AI Studio API key format. Expected prefix 'AQ...' or 'AIza...'"
        )
    gemini_director.set_api_key(key)
    logger.info("Google AI Studio API key updated successfully.")
    return {
        "status": "connected",
        "message": "Google AI Studio API key validated and activated successfully!"
    }


@router.post("/storyboard", response_model=StoryboardResult)
async def create_timestamped_storyboard(req: StoryboardRequest):
    """
    Submits a script to Gemini Pro to generate a timestamped storyboard
    with character actions, camera movements, and AI video prompts.
    """
    if req.api_key and req.api_key.strip():
        gemini_director.set_api_key(req.api_key.strip())

    try:
        storyboard = await gemini_director.analyze_and_build_storyboard(
            raw_script=req.script,
            animation_style=req.animation_style
        )
        return storyboard
    except Exception as e:
        logger.error(f"Failed to generate storyboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate")
async def generate_animated_video(req: GenerateVideoRequest, background_tasks: BackgroundTasks):
    """
    Kicks off full-motion animated AI video rendering from a timestamped storyboard.
    """
    job_id = str(uuid.uuid4())
    output_dir = storage.get_job_dir(job_id)

    GOOGLE_JOBS[job_id] = {
        "job_id": job_id,
        "status": "rendering",
        "progress": 15,
        "stage": "synthesizing_animated_scenes",
        "title": req.storyboard.title,
        "result": None,
        "error": None
    }

    async def _run_veo_pipeline():
        try:
            GOOGLE_JOBS[job_id]["progress"] = 35
            result = await google_veo_engine.render_storyboard_to_video(
                storyboard=req.storyboard,
                output_dir=output_dir,
                voice=req.voice,
                aspect_ratio=req.aspect_ratio,
                burn_captions=req.burn_captions,
                api_key=req.api_key
            )
            GOOGLE_JOBS[job_id]["status"] = "succeeded"
            GOOGLE_JOBS[job_id]["progress"] = 100
            GOOGLE_JOBS[job_id]["stage"] = "completed"
            GOOGLE_JOBS[job_id]["result"] = result
            logger.info(f"Google AI Studio Video Job {job_id} completed successfully!")
        except Exception as e:
            logger.error(f"Google AI Studio Video Job {job_id} failed: {e}")
            GOOGLE_JOBS[job_id]["status"] = "failed"
            GOOGLE_JOBS[job_id]["error"] = str(e)

    background_tasks.add_task(_run_veo_pipeline)

    return {
        "job_id": job_id,
        "status": "rendering",
        "progress": 15,
        "stage": "synthesizing_animated_scenes",
        "title": req.storyboard.title
    }


@router.get("/jobs/{job_id}")
async def get_google_job_status(job_id: str):
    """Polls real-time rendering status for a Google AI Studio video job."""
    if job_id not in GOOGLE_JOBS:
        raise HTTPException(status_code=404, detail="Job not found")
    return GOOGLE_JOBS[job_id]
