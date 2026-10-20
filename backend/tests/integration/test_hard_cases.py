"""Integration Tests for Mandatory Hard Cases (Sections 11, 14, and Hard Cases Matrix)."""
from pathlib import Path
import pytest
from app.services.scene_planner import scene_planner
from app.services.footage_selector import footage_selector
from app.models.job import Job
from app.core.database import AsyncSessionLocal
from app.workers.job_runner import job_runner
from sqlalchemy import select


@pytest.mark.asyncio
async def test_hard_case_abstract_and_statistics():
    # 1. Abstract
    sc_abs = scene_planner.plan_scenes(
        script_or_transcript="Trust is earned slowly through dedicated actions.",
        total_duration=5.0,
        timing_cues=[]
    )
    assert len(sc_abs) == 1
    assert sc_abs[0].category == "abstract_concept"

    selected_abs = await footage_selector.select_footage_for_scenes(sc_abs)
    # Abstract should route to Procedural Generative Engine (ADV-1)
    assert selected_abs[0].provider_chosen == "procedural_gen"
    assert selected_abs[0].clip.is_ai_generated is True

    # 2. Statistics
    sc_stat = scene_planner.plan_scenes(
        script_or_transcript="Enterprise sales grew 40% in 2025 across all primary markets.",
        total_duration=5.0,
        timing_cues=[]
    )
    assert sc_stat[0].category == "data_statistics"
    selected_stat = await footage_selector.select_footage_for_scenes(sc_stat)
    assert selected_stat[0].relevance_score >= 3.5


@pytest.mark.asyncio
async def test_hard_case_double_meanings():
    # Tech cloud vs sky cloud
    sc_tech = scene_planner.plan_scenes(
        script_or_transcript="Deploying server clusters to the cloud computing platform.",
        total_duration=4.0,
        timing_cues=[]
    )
    assert "server" in sc_tech[0].visual_intent or "cloud computing" in sc_tech[0].visual_intent

    # Finance bank vs river bank
    sc_fin = scene_planner.plan_scenes(
        script_or_transcript="Deposit your money into the savings bank account.",
        total_duration=4.0,
        timing_cues=[]
    )
    assert "savings" in sc_fin[0].visual_intent or "currency" in sc_fin[0].visual_intent

    # Code python vs animal
    sc_py = scene_planner.plan_scenes(
        script_or_transcript="Our developer wrote clean python software code.",
        total_duration=4.0,
        timing_cues=[]
    )
    assert "software" in sc_py[0].visual_intent or "code" in sc_py[0].visual_intent


@pytest.mark.asyncio
async def test_hard_case_named_entities_and_sensitive_news():
    sc_named = scene_planner.plan_scenes(
        script_or_transcript="Elon Musk visited Apple headquarters after the tragic grief disaster.",
        total_duration=5.0,
        timing_cues=[]
    )
    notes = sc_named[0].safety_notes
    assert any("NAMED_PERSON_DETECTED" in n for n in notes)
    assert any("BRAND_DETECTED" in n for n in notes)
    assert any("SENSITIVE_CONTENT_DETECTED" in n for n in notes)


@pytest.mark.asyncio
async def test_hard_case_silent_audio(test_db):
    job_id = "test-silent-audio-job"
    async with AsyncSessionLocal() as session:
        job = Job(
            id=job_id,
            status="queued",
            progress=0,
            current_stage="queued",
            input_type="audio",
            input_payload={"audio_url": "tests/fixtures/audio/silent.wav"},
            options={"aspect_ratios": ["16:9"]}
        )
        session.add(job)
        await session.commit()

    await job_runner.run_job(job_id)

    async with AsyncSessionLocal() as session:
        stmt = select(Job).where(Job.id == job_id)
        res = await session.execute(stmt)
        j = res.scalar_one()
        assert j.status == "failed"
        assert j.error_code == "SILENT_AUDIO_DETECTED"


@pytest.mark.asyncio
async def test_hard_case_valid_audio_input(test_db):
    job_id = "test-valid-audio-job"
    async with AsyncSessionLocal() as session:
        job = Job(
            id=job_id,
            status="queued",
            progress=0,
            current_stage="queued",
            input_type="audio",
            input_payload={"audio_url": "tests/fixtures/audio/sample_voiceover.wav"},
            options={"aspect_ratios": ["16:9"]}
        )
        session.add(job)
        await session.commit()

    await job_runner.run_job(job_id)

    async with AsyncSessionLocal() as session:
        stmt = select(Job).where(Job.id == job_id)
        res = await session.execute(stmt)
        j = res.scalar_one()
        assert j.status == "succeeded", f"Job failed: {j.error_message}"
