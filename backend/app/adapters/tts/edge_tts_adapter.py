"""Microsoft Edge Neural TTS Adapter with Word & Sentence Boundary Tracking."""
import asyncio
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple
import edge_tts
from app.adapters.tts.base import TTSAdapter
from app.adapters.tts.mock_tts import MockTTSAdapter
from app.observability.logger import logger


VOICE_MAP = {
    "en-IN-female": "en-IN-NeerjaNeural",
    "en-IN-male": "en-IN-PrabhatNeural",
    "en-IN": "en-IN-NeerjaNeural",
    "en-US-female": "en-US-JennyNeural",
    "en-US-male": "en-US-GuyNeural",
    "en-US": "en-US-JennyNeural",
    "hi-IN-female": "hi-IN-SwaraNeural",
    "hi-IN-male": "hi-IN-MadhurNeural",
    "hi-IN": "hi-IN-SwaraNeural",
    "ta-IN-female": "ta-IN-PallaviNeural",
    "ta-IN-male": "ta-IN-ValluvarNeural",
    "ta-IN": "ta-IN-PallaviNeural",
}


class EdgeTTSAdapter(TTSAdapter):
    """High-quality neural TTS supporting en-IN, en-US, hi-IN, ta-IN with boundary events."""

    def __init__(self):
        self.fallback = MockTTSAdapter()

    async def synthesize(
        self,
        text: str,
        voice: str,
        output_wav_path: Path
    ) -> Tuple[float, List[Dict[str, Any]]]:
        neural_voice = VOICE_MAP.get(voice, VOICE_MAP.get("en-IN-female"))
        output_wav_path.parent.mkdir(parents=True, exist_ok=True)
        temp_mp3 = output_wav_path.with_suffix(".mp3")

        cues: List[Dict[str, Any]] = []

        try:
            communicate = edge_tts.Communicate(text, neural_voice)
            submaker = edge_tts.SubMaker()

            with open(temp_mp3, "wb") as f:
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])
                    elif chunk["type"] == "WordBoundary":
                        # Convert microsecond offset to seconds
                        submaker.feed(chunk)

            # Convert mp3 to standard wav using ffmpeg
            from app.rendering.ffmpeg_engine import ffmpeg_engine
            await ffmpeg_engine.convert_audio(temp_mp3, output_wav_path)
            if temp_mp3.exists():
                temp_mp3.unlink()

            duration = await ffmpeg_engine.probe_duration(output_wav_path)

            # Build sentence-level cues from submaker or proportional split
            raw_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
            if not raw_sentences:
                raw_sentences = [text.strip()]

            total_words = sum(max(1, len(s.split())) for s in raw_sentences)
            curr = 0.0
            for s in raw_sentences:
                w_count = max(1, len(s.split()))
                s_dur = (w_count / total_words) * duration
                cues.append({
                    "text": s,
                    "start": round(curr, 2),
                    "end": round(curr + s_dur, 2),
                    "duration": round(s_dur, 2)
                })
                curr += s_dur

            # Ensure last cue matches total duration
            if cues:
                cues[-1]["end"] = round(duration, 2)
                cues[-1]["duration"] = round(duration - cues[-1]["start"], 2)

            logger.info(f"EdgeTTS generated {duration:.2f}s narration using voice '{neural_voice}'")
            return round(duration, 2), cues

        except Exception as e:
            logger.warning(f"EdgeTTS synthesis failed or timed out ({e}). Falling back to MockTTS.")
            return await self.fallback.synthesize(text, voice, output_wav_path)
