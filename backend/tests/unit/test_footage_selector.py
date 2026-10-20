"""Unit tests for Footage Selector and Provider Routing."""
import pytest
from app.services.footage_selector import footage_selector
from app.services.scene_planner import PlannedScene


@pytest.mark.asyncio
async def test_zero_repeated_clips():
    # Submit 3 similar scenes that could match the same stock clip
    scenes = [
        PlannedScene(
            scene_index=0,
            narration_text="Save money every day for financial future.",
            start_time=0.0,
            end_time=4.0,
            duration=4.0,
            visual_intent="counting paper currency banknotes",
            category="finance",
            suggested_palette="emerald",
            safety_notes=[],
            avoid_tags=[]
        ),
        PlannedScene(
            scene_index=1,
            narration_text="Put extra money in high yield savings accounts.",
            start_time=4.0,
            end_time=8.0,
            duration=4.0,
            visual_intent="counting paper currency banknotes",
            category="finance",
            suggested_palette="emerald",
            safety_notes=[],
            avoid_tags=[]
        ),
        PlannedScene(
            scene_index=2,
            narration_text="Watch your investment wealth compound over time.",
            start_time=8.0,
            end_time=12.0,
            duration=4.0,
            visual_intent="counting paper currency banknotes",
            category="finance",
            suggested_palette="emerald",
            safety_notes=[],
            avoid_tags=[]
        )
    ]

    selected = await footage_selector.select_footage_for_scenes(scenes)
    assert len(selected) == 3

    # Verify all clip IDs are distinct (ZERO repeats in video - MH-5)
    clip_ids = [rec.clip.clip_id for rec in selected]
    assert len(set(clip_ids)) == len(clip_ids), f"Duplicate clips detected: {clip_ids}"


@pytest.mark.asyncio
async def test_dual_provider_routing():
    # Abstract category should route to Procedural Generative engine (ADV-1)
    scenes = [
        PlannedScene(
            scene_index=0,
            narration_text="Trust and philosophical principles form our foundation.",
            start_time=0.0,
            end_time=5.0,
            duration=5.0,
            visual_intent="abstract foundation",
            category="abstract_concept",
            suggested_palette="amber",
            safety_notes=[],
            avoid_tags=[]
        ),
        PlannedScene(
            scene_index=1,
            narration_text="Our servers run in modern cloud computing facilities.",
            start_time=5.0,
            end_time=10.0,
            duration=5.0,
            visual_intent="cloud computing server room with blinking led lights",
            category="technology",
            suggested_palette="cyan",
            safety_notes=[],
            avoid_tags=[]
        )
    ]

    selected = await footage_selector.select_footage_for_scenes(scenes)
    assert selected[0].provider_chosen == "procedural_gen"
    assert selected[0].clip.is_ai_generated is True
    assert selected[1].provider_chosen == "curated_stock"
    assert selected[1].clip.is_ai_generated is False
