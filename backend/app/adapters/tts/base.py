"""Abstract Base Class for Text-to-Speech Adapters."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Tuple


class TTSAdapter(ABC):
    """Abstract interface for narration audio generation."""

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice: str,
        output_wav_path: Path
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Synthesizes speech from text.
        Returns:
            (total_duration_sec, list_of_timing_cues)
            Each timing cue has: {"text": str, "start": float, "end": float}
        """
        pass
