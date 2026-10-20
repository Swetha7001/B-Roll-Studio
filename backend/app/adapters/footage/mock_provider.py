"""Deterministic Mock Footage Provider for fast, reliable offline testing."""
from pathlib import Path
from typing import Any, Dict, List, Optional
from app.adapters.footage.base import FootageClip, FootageProvider
from app.adapters.footage.stock_provider import CURATED_CATALOG


class DeterministicMockProvider(FootageProvider):
    """Reliable offline footage provider for automated unit and integration tests."""

    def __init__(self):
        catalog_items = []
        for item in CURATED_CATALOG:
            d = dict(item)
            if "provider" not in d:
                d["provider"] = "deterministic_mock"
            catalog_items.append(FootageClip(**d))
        self.catalog = catalog_items

    async def search(
        self,
        query: str,
        visual_intent: str,
        target_duration: float,
        aspect_ratio: str = "16:9",
        avoid: Optional[List[str]] = None
    ) -> List[FootageClip]:
        # Return deterministic matches
        q = (query + " " + visual_intent).lower()
        avoid_set = set(a.lower().strip() for a in (avoid or []))

        candidates = []
        for c in self.catalog:
            if any(av in c.title.lower() or av in c.tags for av in avoid_set):
                continue
            candidates.append(c)

        if not candidates:
            return [self.catalog[0]]
        return candidates

    async def get_clip_by_id(self, clip_id: str) -> Optional[FootageClip]:
        for c in self.catalog:
            if c.clip_id == clip_id:
                return c
        return None
