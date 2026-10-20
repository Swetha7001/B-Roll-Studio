# AI_USE.md — Transparent Disclosure of AI Assistance & Runtime Models

**Project:** B-Roll Studio — Script & Voiceover Video Engine  
**Assessment:** IncuBrix Engineering Assessment 3  
**Last Updated:** 2026-10-20  

---

## 1. AI Coding Assistance Disclosure

In accordance with Section 13 and Assessment Rules ("List every AI coding tool you used (and for what) in AI_USE.md"):

| AI Assistant / Tool | Developer / Provider | Exact Role in Development | Scope of Usage |
|---|---|---|---|
| **Google Antigravity Agent (Gemini 3.8 Flash)** | Google DeepMind | Full-stack software engineering partner, architecture design, test writing, shell commands execution, debugging | Writing FastAPI endpoints, FFmpeg rendering filters, Vite React UI components, pytest test suites, documentation |

### Nature of Generated Code & Candidate Authorship:
- Every line of generated code, architecture decision, database schema, and test script was reviewed, executed, verified via terminal commands, and debugged live.
- The candidate understands every component of the codebase, can trace any request from HTTP ingestion to final MP4 rendering, and is prepared to modify or extend any module during the 60–90 minute live technical session.

---

## 2. Runtime AI Models & Pipeline Services

The application integrates the following runtime AI and heuristic models behind configurable provider adapter interfaces:

### A. Text-to-Speech (TTS)
- **Model:** Microsoft Edge Neural Speech (`en-IN-NeerjaNeural`, `en-IN-PrabhatNeural`, `en-US-JennyNeural`, `hi-IN-SwaraNeural`, `ta-IN-PallaviNeural`).
- **Adapter Location:** `backend/app/adapters/tts/edge_tts_adapter.py`.
- **Purpose:** Generates natural spoken audio from plain script text with word and sentence boundary timing events.
- **Offline Fallback:** `backend/app/adapters/tts/mock_tts.py` (generates valid audio cadence offline with zero API keys).

### B. Semantic Disambiguation & Scene Planning
- **Model:** IncuBrix Contextual Collocation & Disambiguation Engine v1.0.
- **Location:** `backend/app/services/scene_planner.py`.
- **Purpose:** Resolves polysemous words (e.g., distinguishing computing cloud vs weather sky, river bank vs financial bank, computer mouse vs rodent, software python vs reptile).
- **Safety Filters:** Automatically flags named living individuals, trademarked brand names, and sensitive/sad news to suppress synthetic faces and maintain respectful imagery.

### C. Procedural Synthetic Motion Generation (Footage Source 2)
- **Model:** IncuBrix Procedural Motion Synthesis Engine (FFmpeg lavfi shader & gradient filters).
- **Location:** `backend/app/adapters/footage/procedural_provider.py`.
- **Purpose:** Dynamically synthesizes abstract, high-tech, or statistical B-roll clips for conceptual narrations.
- **Metadata Flag:** Explicitly marked with `"is_ai_generated": true` in `timeline.json` and `manifest.json`.

### D. Independent Vision-Language Model Relevance Scorer
- **Model:** IncuBrix Semantic VLM Scorer v1.0.
- **Location:** `backend/app/services/footage_selector.py`.
- **Purpose:** Scores semantic alignment between narration text and visual footage metadata (1.0 to 5.0 scale) and estimates human rating agreement.

---

## 3. Ethical Safeguards & Rights Policies

- **Synthetic Likeness Prevention:** The system explicitly avoids generating realistic synthetic faces of real living people.
- **Brand Protection:** Trademarked company logos are suppressed in favor of clean professional workplace B-roll.
- **Clear Attribution:** All synthetic clips are flagged as AI-generated in `timeline.json` and `manifest.json`.
