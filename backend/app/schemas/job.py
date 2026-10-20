"""Pydantic schemas for Job request, response, and timeline outputs."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl, model_validator


class SceneInputItem(BaseModel):
    text: str = Field(..., min_length=1, description="Narration line for the scene")
    visual_hint: Optional[str] = Field(None, description="Optional visual guideline for footage matching")


class CaptionsConfig(BaseModel):
    burn_in: bool = Field(True, description="Whether captions are burned into the video")
    srt: bool = Field(True, description="Whether an SRT subtitle file is generated")


class JobCreateRequest(BaseModel):
    audio_url: Optional[str] = Field(None, description="URL of pre-recorded voiceover (mp3, wav, m4a)")
    script: Optional[str] = Field(None, description="Text script for automatic narration generation")
    scenes: Optional[List[SceneInputItem]] = Field(None, description="Structured IncuBrix scene list")
    
    voice: Optional[str] = Field("en-IN-female", description="Narration voice for TTS")
    aspect_ratios: List[str] = Field(default_factory=lambda: ["16:9", "9:16"], description="Aspect ratios to render (16:9, 9:16, 1:1)")
    style: Optional[str] = Field("bright, modern, real-world footage", description="Visual style direction")
    avoid: List[str] = Field(default_factory=list, description="Content elements to strictly avoid")
    captions: CaptionsConfig = Field(default_factory=CaptionsConfig)
    callback_url: Optional[str] = Field(None, description="Webhook URL for signed completion callback")

    @model_validator(mode="after")
    def validate_inputs(self):
        has_audio = bool(self.audio_url and self.audio_url.strip())
        has_script = bool(self.script and self.script.strip())
        has_scenes = bool(self.scenes and len(self.scenes) > 0)

        if not (has_audio or has_script or has_scenes):
            raise ValueError("At least one input must be provided: audio_url, script, or scenes.")

        # Validate aspect ratios
        valid_ratios = {"16:9", "9:16", "1:1"}
        for r in self.aspect_ratios:
            if r not in valid_ratios:
                raise ValueError(f"Invalid aspect ratio '{r}'. Must be one of: 16:9, 9:16, 1:1")

        return self


class ErrorInfo(BaseModel):
    code: str
    message: str
    retryable: bool = False
    details: Optional[Dict[str, Any]] = None


class JobResultLinks(BaseModel):
    video_16_9: Optional[str] = None
    video_9_16: Optional[str] = None
    video_1_1: Optional[str] = None
    captions_srt: Optional[str] = None
    timeline_json: Optional[str] = None
    manifest_json: Optional[str] = None
    audio_narration: Optional[str] = None


class JobStatusResponse(BaseModel):
    job_id: str
    status: str  # queued, running, succeeded, failed
    progress: int  # 0 to 100
    current_stage: str
    created_at: datetime
    updated_at: datetime
    result: Optional[JobResultLinks] = None
    error: Optional[ErrorInfo] = None


class JobResultResponse(BaseModel):
    job_id: str
    status: str
    aspect_ratios: List[str]
    artifacts: Dict[str, str]
    manifest: Optional[Dict[str, Any]] = None
    timeline: Optional[Dict[str, Any]] = None
    cost_estimate_usd: float = 0.0
    processing_duration_sec: float = 0.0


class SceneSwapRequest(BaseModel):
    scene_index: int = Field(..., ge=0, description="0-based index of the scene to swap")
    new_clip_id: Optional[str] = Field(None, description="Specific replacement clip ID")
    new_visual_hint: Optional[str] = Field(None, description="New visual search hint")
    new_provider: Optional[str] = Field(None, description="Specific footage provider to draw from")
