"""Offline Deterministic Mock TTS Adapter for testing and fallback."""
import math
import re
import struct
import wave
from pathlib import Path
from typing import Any, Dict, List, Tuple
from app.adapters.tts.base import TTSAdapter
from app.observability.logger import logger


class MockTTSAdapter(TTSAdapter):
    """Generates valid WAV audio offline with zero external network or keys."""

    async def synthesize(
        self,
        text: str,
        voice: str,
        output_wav_path: Path
    ) -> Tuple[float, List[Dict[str, Any]]]:
        output_wav_path.parent.mkdir(parents=True, exist_ok=True)

        # Split into sentences or clauses
        raw_sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        if not raw_sentences:
            raw_sentences = [text.strip()]

        sample_rate = 24000
        words_per_sec = 2.5  # Natural speech tempo
        cues: List[Dict[str, Any]] = []
        current_time = 0.0

        # Precompute duration for each sentence
        sentence_timings = []
        for s in raw_sentences:
            word_count = max(1, len(s.split()))
            duration = max(1.8, word_count / words_per_sec)
            sentence_timings.append((s, current_time, current_time + duration, duration))
            cues.append({
                "text": s,
                "start": round(current_time, 2),
                "end": round(current_time + duration, 2),
                "duration": round(duration, 2)
            })
            current_time += duration + 0.3  # pause between sentences

        total_duration = max(1.0, current_time)
        total_samples = int(sample_rate * total_duration)

        # Generate audio buffer (speech formant simulation)
        # Using 16-bit PCM mono
        with wave.open(str(output_wav_path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)

            # Generate in chunks
            chunk_size = 4800
            for i in range(0, total_samples, chunk_size):
                samples_to_write = min(chunk_size, total_samples - i)
                frames = bytearray()
                for j in range(samples_to_write):
                    t = (i + j) / sample_rate
                    # Check if within any active sentence
                    active = False
                    for _, start, end, _ in sentence_timings:
                        if start <= t <= end:
                            active = True
                            break
                    
                    if active:
                        # Soft harmonic voice-like formant tone (150Hz fundamental + 450Hz formant)
                        val = 0.25 * math.sin(2 * math.pi * 150 * t) + 0.15 * math.sin(2 * math.pi * 450 * t)
                        # Envelope
                        amp = int(val * 16000)
                    else:
                        # Gentle background comfort noise / silence
                        amp = 0
                    
                    # Clamp to int16
                    amp = max(-32767, min(32767, amp))
                    frames.extend(struct.pack("<h", amp))
                wav_file.writeframes(frames)

        logger.info(f"MockTTS generated {total_duration:.2f}s audio at {output_wav_path}")
        return round(total_duration, 2), cues
