"""Unit tests for Semantic Scene Planner and Disambiguation."""
import pytest
from app.schemas.job import SceneInputItem
from app.services.scene_planner import scene_planner


def test_disambiguation_cloud():
    # Tech cloud
    scenes_tech = scene_planner.plan_scenes(
        script_or_transcript="Our cloud computing database server runs in the cloud.",
        total_duration=6.0,
        timing_cues=[]
    )
    assert len(scenes_tech) > 0
    assert "server" in scenes_tech[0].visual_intent or "cloud computing" in scenes_tech[0].visual_intent

    # Nature sky cloud
    scenes_nature = scene_planner.plan_scenes(
        script_or_transcript="Look at the natural white clouds in the blue sky.",
        total_duration=6.0,
        timing_cues=[]
    )
    assert "sky" in scenes_nature[0].visual_intent or "natural" in scenes_nature[0].visual_intent


def test_disambiguation_bank():
    # Financial bank
    scenes_fin = scene_planner.plan_scenes(
        script_or_transcript="Deposit your money into the savings bank account.",
        total_duration=6.0,
        timing_cues=[]
    )
    assert "savings" in scenes_fin[0].visual_intent or "currency" in scenes_fin[0].visual_intent

    # River bank
    scenes_river = scene_planner.plan_scenes(
        script_or_transcript="We sat peacefully on the grassy river bank near the water.",
        total_duration=6.0,
        timing_cues=[]
    )
    assert "river" in scenes_river[0].visual_intent


def test_disambiguation_python():
    # Software Python
    scenes_code = scene_planner.plan_scenes(
        script_or_transcript="The developer wrote backend python code with fastapi.",
        total_duration=6.0,
        timing_cues=[]
    )
    assert "software" in scenes_code[0].visual_intent or "code" in scenes_code[0].visual_intent


def test_abstract_and_statistics():
    # Abstract
    scenes_abstract = scene_planner.plan_scenes(
        script_or_transcript="Trust is earned slowly through dedicated actions.",
        total_duration=6.0,
        timing_cues=[]
    )
    assert "craftsman" in scenes_abstract[0].visual_intent or "foundation" in scenes_abstract[0].visual_intent or "handshake" in scenes_abstract[0].visual_intent

    # Numbers
    scenes_stats = scene_planner.plan_scenes(
        script_or_transcript="Company revenue grew 40% in 2025.",
        total_duration=6.0,
        timing_cues=[]
    )
    assert "analytics" in scenes_stats[0].visual_intent or "growth" in scenes_stats[0].visual_intent


def test_safety_guardrails():
    scenes = scene_planner.plan_scenes(
        script_or_transcript="Elon Musk announced that Apple and Google are collaborating after the sad crisis.",
        total_duration=6.0,
        timing_cues=[]
    )
    notes = scenes[0].safety_notes
    assert any("NAMED_PERSON_DETECTED" in n for n in notes)
    assert any("BRAND_DETECTED" in n for n in notes)


def test_structured_scenes_input():
    structured = [
        SceneInputItem(text="First scene line about saving.", visual_hint="bank vault with gold coins"),
        SceneInputItem(text="Second scene line about cloud servers.", visual_hint="server rack with blue lights")
    ]
    scenes = scene_planner.plan_scenes(
        script_or_transcript="",
        total_duration=10.0,
        timing_cues=[],
        structured_scenes=structured
    )
    assert len(scenes) == 2
    assert scenes[0].visual_intent == "bank vault with gold coins"
    assert scenes[1].visual_intent == "server rack with blue lights"
    assert scenes[0].start_time == 0.0
    assert scenes[1].end_time == 10.0
