"""Semantic Scene Planning & Disambiguation Engine.

Implements Must-Haves MH-2, MH-5, MH-6 and Advanced Requirements ADV-3, ADV-4.
Handles:
- Double meanings: cloud, bank, value, mouse, python.
- Abstract lines ("trust is earned slowly").
- Numbers and statistics ("sales grew 40% in 2025").
- Named entities & brands with safety guardrails.
- IncuBrix structured scene lists.
- Sensible pacing (no rapid 0.5s cuts).
"""
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
from app.observability.logger import logger
from app.schemas.job import SceneInputItem


@dataclass
class PlannedScene:
    scene_index: int
    narration_text: str
    start_time: float
    end_time: float
    duration: float
    visual_intent: str
    category: str
    suggested_palette: str
    safety_notes: List[str]
    avoid_tags: List[str]


class ScenePlanner:
    """Plans semantic scenes timed accurately to voiceover narration."""

    # Disambiguation rules based on contextual collocations
    DISAMBIGUATION_RULES = [
        {
            "word": r"\bcloud\b",
            "tech_signals": [
                "computing", "server", "aws", "azure", "data", "storage", "tech", "cluster", "saas", "api",
                "system", "systems", "automated", "deploy", "deploying", "software", "platform", "infrastructure",
                "network", "security", "protect", "business", "revenue", "architecture", "digital"
            ],
            "tech_intent": "cloud computing server room with blinking led lights and network rack",
            "nature_intent": "clear blue sky with soft white clouds"
        },
        {
            "word": r"\bbank\b",
            "fin_signals": ["money", "save", "saving", "account", "finance", "loan", "interest", "deposit", "rate", "cash"],
            "fin_intent": "financial savings growth and currency banknotes",
            "nature_intent": "green grassy river bank with flowing water"
        },
        {
            "word": r"\bvalue\b",
            "ethics_signals": ["trust", "culture", "core", "integrity", "principle", "respect", "relationship", "belief"],
            "ethics_intent": "architectural foundation and business partners shaking hands with mutual trust",
            "fin_intent": "counting investment returns and financial assets",
            "nature_intent": "architectural foundation and business partners shaking hands with mutual trust"
        },
        {
            "word": r"\bmouse\b",
            "tech_signals": ["computer", "click", "screen", "desk", "keyboard", "software", "work", "pc"],
            "tech_intent": "professional using computer mouse at modern office desk",
            "nature_intent": "small wild field mouse in nature"
        },
        {
            "word": r"\bpython\b",
            "tech_signals": ["code", "programming", "developer", "script", "software", "language", "django", "fastapi"],
            "tech_intent": "software engineer typing code in dark theme IDE",
            "nature_intent": "exotic python snake in natural habitat"
        }
    ]

    # Sensitive or sad news signals
    SENSITIVE_SIGNALS = ["tragedy", "died", "loss", "grief", "earthquake", "disaster", "funeral", "sad", "crisis", "victim"]

    # Named people and brand patterns
    NAMED_ENTITIES = ["elon musk", "steve jobs", "sundar pichai", "bill gates", "satya nadella", "tim cook", "mark zuckerberg"]
    BRAND_ENTITIES = ["apple", "google", "microsoft", "amazon", "meta", "tesla", "netflix", "openai"]

    def plan_scenes(
        self,
        script_or_transcript: str,
        total_duration: float,
        timing_cues: List[Dict[str, Any]],
        structured_scenes: Optional[List[SceneInputItem]] = None,
        avoid: Optional[List[str]] = None,
        style: str = "modern"
    ) -> List[PlannedScene]:
        avoid = avoid or []
        planned: List[PlannedScene] = []

        # Case A: Structured scenes provided directly (ADV-4)
        if structured_scenes and len(structured_scenes) > 0:
            num_scenes = len(structured_scenes)
            # Allocate duration across structured scenes
            # If timing cues match structured scenes count, use cue timings
            curr_time = 0.0
            avg_duration = total_duration / num_scenes
            
            for idx, sc in enumerate(structured_scenes):
                if idx < len(timing_cues):
                    s_start = timing_cues[idx]["start"]
                    s_end = timing_cues[idx]["end"]
                else:
                    s_start = round(curr_time, 2)
                    s_end = round(curr_time + avg_duration, 2) if idx < num_scenes - 1 else round(total_duration, 2)

                s_dur = round(max(1.8, s_end - s_start), 2)
                curr_time = s_end

                intent, cat, palette, notes = self._analyze_text_intent(sc.text, sc.visual_hint)
                planned.append(PlannedScene(
                    scene_index=idx,
                    narration_text=sc.text,
                    start_time=s_start,
                    end_time=s_end,
                    duration=s_dur,
                    visual_intent=intent,
                    category=cat,
                    suggested_palette=palette,
                    safety_notes=notes,
                    avoid_tags=avoid
                ))
            return planned

        # Case B: Derive scenes from timing cues (sentences/phrases)
        if not timing_cues:
            # Fallback split
            raw = [s.strip() for s in re.split(r'(?<=[.!?])\s+', script_or_transcript) if s.strip()]
            if not raw:
                raw = [script_or_transcript.strip()]
            avg_dur = total_duration / len(raw)
            c = 0.0
            for s in raw:
                timing_cues.append({
                    "text": s,
                    "start": round(c, 2),
                    "end": round(c + avg_dur, 2),
                    "duration": round(avg_dur, 2)
                })
                c += avg_dur

        # Merge ultra-short cues (< 1.8s) to prevent jarring pacing (ADV-3)
        merged_cues: List[Dict[str, Any]] = []
        for cue in timing_cues:
            if not merged_cues:
                merged_cues.append(dict(cue))
            else:
                last = merged_cues[-1]
                # If last cue is too short or current cue is too short, merge
                if (last["end"] - last["start"] < 2.0) or (cue["end"] - cue["start"] < 1.5):
                    last["text"] = f"{last['text']} {cue['text']}"
                    last["end"] = cue["end"]
                    last["duration"] = round(last["end"] - last["start"], 2)
                else:
                    merged_cues.append(dict(cue))

        # Ensure full duration coverage (MH-2: every second of narration is covered)
        if merged_cues:
            merged_cues[0]["start"] = 0.0
            merged_cues[-1]["end"] = round(total_duration, 2)
            merged_cues[-1]["duration"] = round(total_duration - merged_cues[-1]["start"], 2)

        for idx, cue in enumerate(merged_cues):
            text = cue["text"]
            start_t = cue["start"]
            end_t = cue["end"]
            dur = round(end_t - start_t, 2)

            intent, cat, palette, notes = self._analyze_text_intent(text)
            planned.append(PlannedScene(
                scene_index=idx,
                narration_text=text,
                start_time=start_t,
                end_time=end_t,
                duration=dur,
                visual_intent=intent,
                category=cat,
                suggested_palette=palette,
                safety_notes=notes,
                avoid_tags=avoid
            ))

        return planned

    def _analyze_text_intent(self, text: str, user_hint: Optional[str] = None) -> Tuple[str, str, str, List[str]]:
        """Extracts semantic visual intent, disambiguating ambiguous phrases and guarding safety."""
        lower_text = text.lower()
        notes: List[str] = []

        # 1. Safety & Brand / People Guardrails (MH-6)
        for person in self.NAMED_ENTITIES:
            if person in lower_text:
                notes.append(f"NAMED_PERSON_DETECTED: '{person}'. Suppressing AI realistic face synthesis; using neutral industry B-roll.")
        for brand in self.BRAND_ENTITIES:
            if brand in lower_text:
                notes.append(f"BRAND_DETECTED: '{brand}'. Avoiding trademarked logos; using generic professional tech footage.")
        for sad_word in self.SENSITIVE_SIGNALS:
            if sad_word in lower_text:
                notes.append(f"SENSITIVE_CONTENT_DETECTED: '{sad_word}'. Using respectful, subdued palette and calm imagery.")

        # If user explicitly provided visual hint, prioritize it
        if user_hint and user_hint.strip():
            return user_hint.strip(), "ai_scene", "cyan", notes

        # 2. Check for Disambiguation rules
        for rule in self.DISAMBIGUATION_RULES:
            if re.search(rule["word"], lower_text):
                signals = rule.get("tech_signals") or rule.get("fin_signals") or rule.get("ethics_signals") or []
                if any(sig in lower_text for sig in signals):
                    intent = rule.get("tech_intent") or rule.get("fin_intent") or rule.get("ethics_intent")
                    palette = "cyan" if "tech" in rule else ("emerald" if "fin" in rule else "amber")
                    return intent, "disambiguated_specific", palette, notes
                else:
                    default_intent = rule.get("nature_intent") or rule.get("fin_intent") or "modern professional footage"
                    return default_intent, "disambiguated_default", "cyan", notes

        # 3. Check for Abstract lines ("trust is earned slowly", "values matter")
        if any(w in lower_text for w in ["trust", "earn", "slowly", "relationship", "reputation", "foundation"]):
            return "craftsman building stone foundation and firm professional handshake", "abstract_concept", "amber", notes

        # 4. Check for Numbers / Statistics ("sales grew 40% in 2025")
        if re.search(r'\d+%', lower_text) or any(w in lower_text for w in ["sales", "grow", "growth", "revenue", "metric", "statistic", "kpi"]):
            return "analytics dashboard showing upward line graph and quarterly growth metrics", "data_statistics", "violet", notes

        # 5. Finance / Money Saving
        if any(w in lower_text for w in ["money", "save", "saving", "budget", "finance", "dollar", "wealth"]):
            return "counting paper currency and saving coins into wealth portfolio", "finance", "emerald", notes

        # 6. Technology / Software
        if any(w in lower_text for w in ["code", "software", "tech", "data", "server", "algorithm", "developer"]):
            return "modern enterprise server room with blinking led lights and software engineer", "technology", "cyan", notes

        # 7. Sensitive / Somber News
        if any(w in lower_text for w in self.SENSITIVE_SIGNALS):
            return "subdued, respectful landscape with quiet evening light", "sensitive_news", "slate", notes

        # Default fallback
        return f"modern professional footage illustrating: {text[:45]}", "general_lifestyle", "slate", notes


scene_planner = ScenePlanner()
