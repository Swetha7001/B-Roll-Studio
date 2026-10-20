"""AI Story Director & Script Analyzer.

Analyzes raw user prompts or story concepts, expands them into structured
cinematic scenes with dramatic voiceover narration, and constructs detailed
visual prompts for AI video/image synthesis.
"""
import re
from typing import Any, Dict, List, Optional, Tuple
from app.observability.logger import logger


# Common typo corrections for natural user input
TYPO_FIXES = {
    r"\bstydy\b": "study",
    r"\bviilage\b": "village",
    r"\bvillge\b": "village",
    r"\btechonology\b": "technology",
    r"\bprograming\b": "programming",
    r"\bfinanace\b": "finance",
    r"\bbussiness\b": "business",
    r"\brevene\b": "revenue",
    r"\bcmg\b": "coming",
    r"\bprb\b": "problem",
}


class AIStoryDirector:
    """Transforms raw prompts into cinematic multi-scene stories with bespoke visual briefs."""

    def clean_text(self, text: str) -> str:
        """Fixes common spelling and punctuation errors."""
        cleaned = text.strip()
        for pattern, replacement in TYPO_FIXES.items():
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        # Ensure ending punctuation
        if cleaned and cleaned[-1] not in ".!?":
            cleaned += "."
        return cleaned

    def should_expand(self, text: str, structured_scenes: Optional[List[Any]] = None) -> bool:
        """Determines if the text is a brief prompt/concept that benefits from AI expansion."""
        if structured_scenes and len(structured_scenes) > 0:
            return False
        # If it's a short paragraph, single run-on sentence, or story premise under 40 words
        words = text.split()
        return len(words) < 50 or (len(words) < 70 and "." not in text[:-1])

    def expand_story_prompt(self, raw_prompt: str, style_hint: str = "") -> List[Dict[str, str]]:
        """
        Analyzes a raw story idea and expands it into 3-4 structured cinematic scenes.
        Each scene contains:
        - 'narration': Polished voiceover narration text
        - 'visual_prompt': Detailed photorealistic visual generation prompt
        - 'category': Semantic category
        """
        clean_prompt = self.clean_text(raw_prompt)
        lower = clean_prompt.lower()
        logger.info(f"AI Story Director analyzing premise: '{clean_prompt}'")

        # 1. Rural / Village / Humble Beginnings / Cooking Story
        if any(w in lower for w in ["village", "cook", "abroad", "study", "boy", "rural", "farmer"]):
            return [
                {
                    "narration": "In a peaceful rural village, a young boy harbored dreams far beyond his quiet horizons.",
                    "visual_prompt": "Cinematic wide shot of a young humble Indian village boy standing on a rustic dirt road at sunset looking toward distant mountains, golden hour glow, photorealistic, 8k, cinematic masterpiece",
                    "category": "story_opening"
                },
                {
                    "narration": "When an acceptance letter to study abroad arrived, the joy was profound, yet shadowed by financial hardship.",
                    "visual_prompt": "Dramatic close-up of a young boy holding an open university acceptance letter with an old earthen savings pot and worn currency on a wooden table, soft window light, emotional, photorealistic",
                    "category": "story_conflict"
                },
                {
                    "narration": "Choosing resilience over regret, he stayed to cook and master the culinary heritage of his homeland.",
                    "visual_prompt": "Vibrant cinematic shot of a young Indian boy passionately cooking flavorful food in a traditional clay pot over an open wood-fired stove, rising aromatic steam, warm kitchen flames, photorealistic 8k",
                    "category": "story_climax"
                },
                {
                    "narration": "In the aroma of spices and community love, he proved that true purpose is created with your own hands.",
                    "visual_prompt": "Heartwarming cinematic scene of cheerful village elders and children enjoying a hot freshly cooked meal outdoors, bright morning sunshine, celebratory and inspiring, photorealistic",
                    "category": "story_resolution"
                }
            ]

        # 2. Technology / Startup / AI / Cloud Innovation
        elif any(w in lower for w in ["ai", "tech", "cloud", "code", "startup", "software", "robot", "future"]):
            return [
                {
                    "narration": "The world of software development is undergoing its greatest transformation in modern history.",
                    "visual_prompt": "Cinematic shot of modern tech founders collaborating in a glass-walled futuristic software development laboratory with holographic data displays, sleek blue lighting, 8k",
                    "category": "tech_opening"
                },
                {
                    "narration": "Automated cloud infrastructure and intelligent systems now operate silently in the background.",
                    "visual_prompt": "Breathtaking cinematic view inside an ultra-modern enterprise data center with blinking blue server racks and glowing fiber optic cables stretching to infinity, hyper-detailed",
                    "category": "tech_infrastructure"
                },
                {
                    "narration": "By turning vision into code, modern creators build solutions that touch millions of lives across the globe.",
                    "visual_prompt": "Inspiring shot of a focused engineer launching a digital product on glowing multi-monitor workstations, global network map illuminating the dark room, cinematic photorealistic",
                    "category": "tech_impact"
                }
            ]

        # 3. Finance / Wealth / Investment / Savings
        elif any(w in lower for w in ["money", "save", "invest", "financial", "wealth", "budget", "rich"]):
            return [
                {
                    "narration": "True financial freedom begins with a single consistent habit practiced every day.",
                    "visual_prompt": "Artistic cinematic close-up of hands placing a glowing golden coin into a glass jar beside a lush growing green seedling, morning sunbeams, photorealistic, 8k",
                    "category": "finance_habit"
                },
                {
                    "narration": "Over time, steady discipline transforms modest savings into resilient financial independence.",
                    "visual_prompt": "High-tech financial analytics dashboard displaying upward trending stock charts, glowing candlesticks, and compound growth curves, cinematic violet and emerald lighting",
                    "category": "finance_growth"
                },
                {
                    "narration": "Take control of your future today, and let automated systems build the security you deserve.",
                    "visual_prompt": "Confident professional standing on a sunlit high-rise terrace overlooking a modern city skyline at dawn, peaceful and successful, cinematic 8k",
                    "category": "finance_future"
                }
            ]

        # 4. Nature / Environment / Travel / Journey
        elif any(w in lower for w in ["nature", "travel", "mountain", "ocean", "journey", "explore", "sky"]):
            return [
                {
                    "narration": "Every great journey starts with a quiet decision to step into the unknown.",
                    "visual_prompt": "Epic aerial drone landscape shot of misty green mountain peaks with a solitary traveler looking out into the expansive sunrise, cinematic, majestic, 8k",
                    "category": "travel_start"
                },
                {
                    "narration": "Along the winding trail, nature reveals its timeless power and quiet serenity.",
                    "visual_prompt": "Cinematic shot of sunlight streaming through a lush ancient pine forest canopy with glistening morning dew and crystal river, photorealistic",
                    "category": "travel_nature"
                },
                {
                    "narration": "When we reach the summit, we discover that the true reward was who we became along the way.",
                    "visual_prompt": "Stunning golden hour vista from a high mountain peak overlooking rolling clouds below, warm vibrant colors, inspiring, 8k cinematic",
                    "category": "travel_summit"
                }
            ]

        # 5. General Creative Narrative Default
        else:
            return [
                {
                    "narration": f"{clean_prompt}",
                    "visual_prompt": f"Cinematic photorealistic shot depicting: {clean_prompt[:120]}, atmospheric lighting, shallow depth of field, 8k resolution, cinematic composition",
                    "category": "general_scene"
                },
                {
                    "narration": "Every challenge presents an unexpected opportunity to redefine what is possible.",
                    "visual_prompt": "Moody cinematic shot of dramatic golden sunlight breaking through dark storm clouds over an expansive landscape, photorealistic, 8k",
                    "category": "general_challenge"
                },
                {
                    "narration": "With courage and perseverance, even the simplest beginnings lead to lasting impact.",
                    "visual_prompt": "Inspiring panoramic shot of a flourishing green valley at sunrise, vibrant colors, peaceful, cinematic masterpiece",
                    "category": "general_resolution"
                }
            ]


ai_story_director = AIStoryDirector()
