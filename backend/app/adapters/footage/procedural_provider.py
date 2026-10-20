"""Procedural Motion & Generative B-Roll Provider (Source 2).

Implements Advanced Requirement ADV-1 & Must-Have MH-3:
- Fully synthetic/procedural visual graphics.
- Clearly marked with is_ai_generated: True.
- Licenced under Apache 2.0 / Procedural Synthesizer.
"""
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.adapters.footage.base import FootageClip, FootageProvider
from app.rendering.ffmpeg_engine import ffmpeg_engine
from app.observability.logger import logger


class ProceduralGenerativeProvider(FootageProvider):
    """Generative Procedural Motion clip provider."""

    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path("./artifacts/procedural_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    async def search(
        self,
        query: str,
        visual_intent: str,
        target_duration: float,
        aspect_ratio: str = "16:9",
        avoid: Optional[List[str]] = None
    ) -> List[FootageClip]:
        # Determine color scheme based on sentiment or intent
        combined = f"{query} {visual_intent}".lower()
        if any(w in combined for w in ["money", "finance", "grow", "profit", "wealth"]):
            scheme = "emerald"
        elif any(w in combined for w in ["cloud", "tech", "code", "ai", "software", "python", "future"]):
            scheme = "cyan"
        elif any(w in combined for w in ["stat", "number", "metric", "chart", "analysis", "science"]):
            scheme = "violet"
        elif any(w in combined for w in ["trust", "safe", "handshake", "agreement", "secure"]):
            scheme = "amber"
        else:
            scheme = "slate"

        clip_hash = hashlib.md5(f"{combined}_{aspect_ratio}_{scheme}".encode()).hexdigest()[:8]
        clip_id = f"proc-gen-{clip_hash}"
        out_path = self.cache_dir / f"{clip_id}_{aspect_ratio.replace(':', '_')}.mp4"

        # Generate on-demand if not cached
        if not out_path.exists():
            await ffmpeg_engine.generate_procedural_clip(
                output_mp4_path=out_path,
                duration=max(6.0, target_duration),
                title=visual_intent or query,
                aspect_ratio=aspect_ratio,
                color_scheme=scheme
            )

        clip = FootageClip(
            clip_id=clip_id,
            provider="procedural_gen",
            title=f"Synthetic Motion — {visual_intent[:35]}",
            description=f"Procedurally rendered {scheme} motion canvas simulating {visual_intent}",
            duration=target_duration,
            width=1920 if aspect_ratio == "16:9" else 1080,
            height=1080 if aspect_ratio == "16:9" else (1920 if aspect_ratio == "9:16" else 1080),
            aspect_ratio=aspect_ratio,
            source_url="internal://procedural_gen/synthesizer",
            download_url=str(out_path).replace("\\", "/"),
            license_name="IncuBrix Synthetic Generative License (100% Commercial Use Allowed)",
            license_url="internal://licenses/incubrix-synthetic-v1",
            attribution="IncuBrix Procedural Motion Synthesis Engine",
            is_ai_generated=True,
            tags=["synthetic", "motion_graphics", "ai_generated", scheme],
            local_cache_path=out_path
        )
        return [clip]

    async def get_clip_by_id(self, clip_id: str) -> Optional[FootageClip]:
        matches = list(self.cache_dir.glob(f"{clip_id}*.mp4"))
        if matches:
            p = matches[0]
            return FootageClip(
                clip_id=clip_id,
                provider="procedural_gen",
                title="Procedural Motion Asset",
                description="Procedural synthetic motion canvas",
                duration=6.0,
                width=1920,
                height=1080,
                aspect_ratio="16:9",
                source_url="internal://procedural_gen/synthesizer",
                download_url=str(p).replace("\\", "/"),
                license_name="IncuBrix Synthetic Generative License",
                license_url="internal://licenses/incubrix-synthetic-v1",
                attribution="IncuBrix Procedural Motion Synthesis Engine",
                is_ai_generated=True,
                tags=["synthetic"],
                local_cache_path=p
            )
        return None
