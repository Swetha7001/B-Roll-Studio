"""Base types and abstract interface for footage providers."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class FootageClip:
    clip_id: str
    provider: str
    title: str
    description: str
    duration: float
    width: int
    height: int
    aspect_ratio: str
    source_url: str
    download_url: str
    license_name: str
    license_url: str
    attribution: str
    is_ai_generated: bool
    tags: List[str] = field(default_factory=list)
    local_cache_path: Optional[Path] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clip_id": self.clip_id,
            "provider": self.provider,
            "title": self.title,
            "description": self.description,
            "duration": self.duration,
            "width": self.width,
            "height": self.height,
            "aspect_ratio": self.aspect_ratio,
            "source_url": self.source_url,
            "download_url": self.download_url,
            "license_name": self.license_name,
            "license_url": self.license_url,
            "attribution": self.attribution,
            "is_ai_generated": self.is_ai_generated,
            "tags": self.tags,
        }


class FootageProvider(ABC):
    """Abstract footage provider interface."""

    @abstractmethod
    async def search(
        self,
        query: str,
        visual_intent: str,
        target_duration: float,
        aspect_ratio: str = "16:9",
        avoid: Optional[List[str]] = None
    ) -> List[FootageClip]:
        """Searches for clips matching semantic intent."""
        pass

    @abstractmethod
    async def get_clip_by_id(self, clip_id: str) -> Optional[FootageClip]:
        """Retrieves clip metadata by unique identifier."""
        pass
