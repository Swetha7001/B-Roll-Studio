"""End-to-End Pipeline Test with Real FFmpeg Output Verification."""
import asyncio
from pathlib import Path
import pytest
from app.rendering.ffmpeg_engine import ffmpeg_engine
from app.workers.job_runner import job_runner
from app.models.job import Job
from app.core.database import AsyncSessionLocal
from sqlalchemy import select


@pytest.mark.asyncio
async def test_full_pipeline_rendering_e2e(test_db):
    # Setup test job directly
    job_id = "test-e2e-job-001"
    async with AsyncSessionLocal() as session:
        job = Job(
            id=job_id,
            status="queued",
            progress=0,
            current_stage="queued",
            input_type="script",
            input_payload={"script": "Save money automatically every single month. Consistent habits build lasting wealth."},
            options={
                "voice": "en-IN-female",
                "aspect_ratios": ["16:9", "9:16"],
                "captions": {"burn_in": True, "srt": True}
            }
        )
        session.add(job)
        await session.commit()

    # Execute end-to-end processing pipeline
    await job_runner.run_job(job_id)

    # Verify Job succeeded
    async with AsyncSessionLocal() as session:
        stmt = select(Job).where(Job.id == job_id)
        res = await session.execute(stmt)
        completed_job = res.scalar_one()
        assert completed_job.status == "succeeded", f"Job failed with: {completed_job.error_message}"
        assert completed_job.progress == 100

    # Verify actual rendered output files exist on disk
    job_dir = Path("artifacts/storage") / job_id
    assert (job_dir / "timeline.json").exists()
    assert (job_dir / "manifest.json").exists()
    assert (job_dir / "captions.srt").exists()

    video_16_9 = job_dir / "video_16_9.mp4"
    assert video_16_9.exists(), "video_16_9.mp4 must be rendered"
    assert video_16_9.stat().st_size > 10000

    # Probe rendered video with ffprobe to verify codecs, framerate, and duration
    probe_meta = await ffmpeg_engine.probe_media(video_16_9)
    streams = probe_meta.get("streams", [])
    
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

    assert video_stream is not None, "Video stream missing from output file"
    assert video_stream.get("codec_name") == "h264", "Video codec must be H.264"
    assert video_stream.get("width") == 1920
    assert video_stream.get("height") == 1080

    assert audio_stream is not None, "Audio stream missing from output file"
    assert audio_stream.get("codec_name") == "aac", "Audio codec must be AAC"

    dur = await ffmpeg_engine.probe_duration(video_16_9)
    assert dur > 1.0, f"Rendered video duration should be > 1.0s, got {dur}"
