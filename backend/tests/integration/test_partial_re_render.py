"""Integration test for Clip Swap and Accelerated Partial Re-rendering (ADV-2)."""
import time
from pathlib import Path
import pytest
from app.adapters.footage.stock_provider import CuratedStockProvider
from app.core.database import AsyncSessionLocal
from app.models.job import Job
from app.rendering.partial_renderer import partial_renderer
from app.services.footage_selector import footage_selector
from app.services.scene_planner import scene_planner
from app.workers.job_runner import job_runner
from sqlalchemy import select


@pytest.mark.asyncio
async def test_clip_swap_and_partial_re_render(test_db):
    job_id = "test-swap-partial-job-002"
    job_dir = Path("artifacts/storage") / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    # 1. Run initial job
    async with AsyncSessionLocal() as session:
        job = Job(
            id=job_id,
            status="queued",
            progress=0,
            current_stage="queued",
            input_type="script",
            input_payload={"script": "Save money automatically. Deploy cloud servers reliably."},
            options={
                "voice": "en-IN-female",
                "aspect_ratios": ["16:9"],
                "captions": {"burn_in": True, "srt": True}
            }
        )
        session.add(job)
        await session.commit()

    await job_runner.run_job(job_id)

    # Verify initial completion
    async with AsyncSessionLocal() as session:
        stmt = select(Job).where(Job.id == job_id)
        res = await session.execute(stmt)
        j = res.scalar_one()
        assert j.status == "succeeded"

    # 2. Swap clip for Scene 0
    stock_prov = CuratedStockProvider()
    replacement_clip = await stock_prov.get_clip_by_id("stock-work-003")
    assert replacement_clip is not None

    planned_scenes = scene_planner.plan_scenes(
        script_or_transcript="Save money automatically. Deploy cloud servers reliably.",
        total_duration=5.0,
        timing_cues=[]
    )
    selected_clips = await footage_selector.select_footage_for_scenes(planned_scenes)

    narration_wav = job_dir / "narration.wav"
    captions_srt = job_dir / "captions.srt"

    # Execute partial re-render
    artifacts_map, partial_dur, full_dur_est = await partial_renderer.swap_and_re_render(
        job_dir=job_dir,
        job_id=job_id,
        scene_index=0,
        new_clip=replacement_clip,
        planned_scenes=planned_scenes,
        selected_clips=selected_clips,
        aspect_ratios=["16:9"],
        narration_wav=narration_wav,
        captions_srt=captions_srt,
        burn_in_captions=True
    )

    assert "video_16_9" in artifacts_map
    assert "timeline_json" in artifacts_map
    # Verify partial render duration is measurably less than estimated full render duration (ADV-2)
    assert partial_dur < full_dur_est, f"Partial render ({partial_dur}s) must be less than full render ({full_dur_est}s)"
