"""Unit tests for Google AI Video Generation Center (Gemini Director & Veo Engine)."""
import pytest
from app.adapters.google_ai.gemini_director import gemini_director, TimestampedScene
from app.adapters.google_ai.veo_video_engine import google_veo_engine


@pytest.mark.asyncio
async def test_gemini_director_storyboard_generation():
    script = "A boy in a village begins cooking fish curry over open firewood."
    storyboard = await gemini_director.analyze_and_build_storyboard(
        raw_script=script,
        animation_style="3d_animation"
    )

    assert storyboard.title != ""
    assert len(storyboard.scenes) >= 2
    assert storyboard.total_duration_seconds > 0

    first_scene = storyboard.scenes[0]
    assert first_scene.scene_index == 0
    assert first_scene.timestamp_start.startswith("00:")
    assert first_scene.timestamp_end.startswith("00:")
    assert first_scene.character_action != ""
    assert first_scene.camera_movement != ""
    assert "Pixar" in first_scene.visual_prompt or "3D" in first_scene.visual_prompt


@pytest.mark.asyncio
async def test_google_studio_config_and_storyboard_api(async_client):
    # 1. Config endpoint
    resp = await async_client.get("/api/v1/google-studio/config")
    assert resp.status_code == 200
    data = resp.json()
    assert data["gemini_pro_ready"] is True
    assert "google-veo-2.0" in data["supported_models"]
    assert len(data["supported_styles"]) >= 4

    # 2. Storyboard endpoint
    story_resp = await async_client.post(
        "/api/v1/google-studio/storyboard",
        json={
            "script": "A young artist paints a futuristic neon city from a high rooftop in Tokyo.",
            "animation_style": "cyberpunk"
        }
    )
    assert story_resp.status_code == 200
    story_data = story_resp.json()
    assert len(story_data["scenes"]) >= 2
    assert any("cyberpunk" in s["visual_prompt"].lower() or "neon" in s["visual_prompt"].lower() for s in story_data["scenes"])


def test_srt_generation(tmp_path):
    scenes = [
        TimestampedScene(
            scene_index=0,
            timestamp_start="00:00",
            timestamp_end="00:05",
            start_seconds=0.0,
            end_seconds=5.0,
            duration_seconds=5.0,
            narration="In a quiet village, cooking starts at dawn.",
            visual_prompt="Village kitchen morning",
            character_action="Stirring pot",
            camera_movement="Push in"
        ),
        TimestampedScene(
            scene_index=1,
            timestamp_start="00:05",
            timestamp_end="00:10",
            start_seconds=5.0,
            end_seconds=10.0,
            duration_seconds=5.0,
            narration="Aromatic spices sizzle over firewood.",
            visual_prompt="Bubbling spices clay pot",
            character_action="Adding spices",
            camera_movement="Low angle tilt"
        )
    ]

    srt_file = tmp_path / "test.srt"
    google_veo_engine._generate_timestamped_srt(scenes, srt_file)
    content = srt_file.read_text(encoding="utf-8")

    assert "00:00:00,000 --> 00:00:05,000" in content
    assert "In a quiet village, cooking starts at dawn." in content
    assert "00:00:05,000 --> 00:00:10,000" in content
    assert "Aromatic spices sizzle over firewood." in content
