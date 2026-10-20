"""Generates the 10 core evaluation input variants for Section 15 of IncuBrix assessment."""
import json
from pathlib import Path

TEN_INPUTS = [
    {
        "id": "input_01_tutorial",
        "title": "Educational Tutorial: Cloud Computing Architecture",
        "script": "Cloud computing allows developers to deploy applications on global server infrastructure without managing physical hardware. Modern cloud platforms provide scalable databases, automated monitoring, and reliable data storage.",
        "voice": "en-IN-female",
        "aspect_ratios": ["16:9", "9:16"],
        "style": "bright, modern tech",
        "avoid": ["people's faces"],
        "captions": {"burn_in": True, "srt": True}
    },
    {
        "id": "input_02_news_summary",
        "title": "News Summary: Renewable Energy Grid Expansion",
        "script": "State energy regulators announced a landmark milestone today as national renewable generation reached record levels. Government funding will modernize electrical grid transmission across regional networks.",
        "voice": "en-IN-male",
        "aspect_ratios": ["16:9"],
        "style": "journalistic, clean",
        "avoid": ["violence"],
        "captions": {"burn_in": True, "srt": True}
    },
    {
        "id": "input_03_product_promo",
        "title": "Product Promotion: B-Roll Studio Workflow",
        "script": "Transform your creative workflow with automated B-roll generation. Simply type your script, and let artificial intelligence match cinematic, commercial-grade stock footage timed perfectly to your voice.",
        "voice": "en-IN-female",
        "aspect_ratios": ["16:9", "9:16", "1:1"],
        "style": "cinematic, polished",
        "avoid": ["alcohol"],
        "captions": {"burn_in": True, "srt": True}
    },
    {
        "id": "input_04_short_story",
        "title": "Short Narrative: The Founder's Journey",
        "script": "They started in a cramped office with only two laptops and unwavering conviction. Every late night debugging code brought them closer to building something truly enduring.",
        "voice": "en-US-female",
        "aspect_ratios": ["16:9"],
        "style": "inspirational, warm",
        "avoid": [],
        "captions": {"burn_in": True, "srt": True}
    },
    {
        "id": "input_05_abstract_concept",
        "title": "Abstract Concept: Trust & Foundation",
        "script": "Trust is earned slowly through consistent actions and unwavering integrity. When partnerships are built on solid foundations, enduring value naturally follows.",
        "voice": "en-IN-female",
        "aspect_ratios": ["16:9", "9:16"],
        "style": "metaphorical, dignified",
        "avoid": [],
        "captions": {"burn_in": True, "srt": True}
    },
    {
        "id": "input_06_finance_statistics",
        "title": "Financial Statistics: Annual Growth Review",
        "script": "Quarterly enterprise sales grew 40% in 2025 across all primary markets. Disciplined budget allocation and proactive investment management generated strong shareholder returns.",
        "voice": "en-IN-male",
        "aspect_ratios": ["16:9", "1:1"],
        "style": "executive, analytical",
        "avoid": [],
        "captions": {"burn_in": True, "srt": True}
    },
    {
        "id": "input_07_ambiguous_words",
        "title": "Ambiguous Disambiguation: Cloud, Bank, Mouse, Python",
        "script": "We configured our cloud computing servers near the river bank. The developer used a computer mouse to write clean python code for financial wealth growth.",
        "voice": "en-IN-female",
        "aspect_ratios": ["16:9", "9:16"],
        "style": "modern technology",
        "avoid": [],
        "captions": {"burn_in": True, "srt": True}
    },
    {
        "id": "input_08_short_duration",
        "title": "Short Narrative: Rapid Daily Tip",
        "script": "Save money automatically every single payday. Consistent small habits build substantial financial freedom over time.",
        "voice": "en-IN-female",
        "aspect_ratios": ["9:16"],
        "style": "snappy, dynamic",
        "avoid": [],
        "captions": {"burn_in": True, "srt": True}
    },
    {
        "id": "input_09_multilingual_hindi",
        "title": "Multilingual Indian Accent / Hindi Voiceover",
        "script": "बचत करना और सही जगह निवेश करना भविष्य के लिए बहुत जरूरी है। सही वित्तीय योजना आपको आर्थिक स्वतंत्रता प्रदान करती है।",
        "voice": "hi-IN-female",
        "aspect_ratios": ["16:9"],
        "style": "bright, authentic",
        "avoid": [],
        "captions": {"burn_in": True, "srt": True}
    },
    {
        "id": "input_10_structured_scenes",
        "title": "Structured IncuBrix Scene List Input",
        "scenes": [
            {
                "text": "Managing corporate finances requires strategic planning and disciplined saving.",
                "visual_hint": "executive counting currency banknotes and reviewing financial assets"
            },
            {
                "text": "Deploying scalable infrastructure to the cloud protects company data and uptime.",
                "visual_hint": "cloud computing server rack with blinking led lights"
            },
            {
                "text": "True professional partnerships are founded on mutual trust and shared values.",
                "visual_hint": "business partners shaking hands firmly in collaborative office"
            }
        ],
        "voice": "en-IN-female",
        "aspect_ratios": ["16:9", "9:16"],
        "style": "cinematic commercial",
        "avoid": ["people's faces"],
        "captions": {"burn_in": True, "srt": True}
    }
]


def main():
    out_dir = Path("tests/fixtures/inputs")
    out_dir.mkdir(parents=True, exist_ok=True)

    for item in TEN_INPUTS:
        fname = f"{item['id']}.json"
        with open(out_dir / fname, "w", encoding="utf-8") as f:
            json.dump(item, f, indent=2, ensure_ascii=False)
        print(f"Wrote {fname}")

    print(f"\nGenerated all {len(TEN_INPUTS)} test input fixtures successfully.")


if __name__ == "__main__":
    main()
