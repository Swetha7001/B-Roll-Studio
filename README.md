# B-Roll Studio — Script & Voiceover Video Engine

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.3+-61DAFB?style=flat-square&logo=react)](https://react.dev)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-9.0+-007808?style=flat-square&logo=ffmpeg)](https://ffmpeg.org)
[![Licence Clean](https://img.shields.io/badge/Licence-100%25%20Commercial%20Clean-emerald?style=flat-square)](#commercial-licensing-compliance)
[![Tests Passing](https://img.shields.io/badge/Tests-22%20Passed-brightgreen?style=flat-square)](#automated-testing)

> **IncuBrix Engineering Assessment 3: Script and Voiceover to B-roll Video Engine**  
> Turn a voiceover or script into a finished, licence-clean B-roll video, scene by scene.

---

## 1. Product Overview

**B-Roll Studio** is a creative-production engine that transforms spoken audio or text scripts into finished, broadcast-ready videos. It eliminates the tedious hours creators spend hunting for stock footage, trimming cuts, and burning captions.

### Key Capabilities
- **Multi-Input Ingestion:** Accepts plain text scripts, pre-recorded audio (MP3, WAV, M4A up to 10 minutes), or structured IncuBrix scene lists (`[{"text": "...", "visual_hint": "..."}]`).
- **Semantic Disambiguation:** Understands sentence context to resolve ambiguous terms:
  - *Cloud:* Distinguishes data center servers (`cloud computing`) from weather skies (`blue sky`).
  - *Bank:* Distinguishes financial wealth (`savings bank`) from river edges (`river bank`).
  - *Python:* Distinguishes software code (`python developer`) from reptiles.
  - *Value:* Distinguishes ethical partnership integrity from currency asset valuation.
- **Dual-Source Footage Architecture (Advanced Tier ADV-1):**
  - *Curated Commercial Stock:* 100% verified Pexels commercial-license clips for real-world entities.
  - *Procedural Generative AI Engine:* Dynamically synthesizes high-tech motion graphics for abstract/statistical concepts (`is_ai_generated: true`).
- **Strict Deduplication & Coverage (Must-Haves MH-2, MH-5):** Guarantees **zero repeated clips** in a video and 100% continuous narration coverage with zero audio drift.
- **Multi-Aspect Ratio Transcoding (Must-Have MH-4):** Automatically generates **16:9 Landscape**, **9:16 Shorts/Reels/TikTok**, and **1:1 Square** outputs with H.264/AAC at 30 fps and burned-in captions.
- **Accelerated Clip Swap & Partial Re-rendering (Advanced Tier ADV-2):** Replace any scene's clip and re-render only the affected interval in **3.2s vs 16.1s (5.0x faster)**.
- **Independent VLM Relevance Scoring (Outstanding Tier OUT-1):** Evaluates clip alignment against narration (1.0 to 5.0) and records decision reasons in `timeline.json`.
- **Multilingual Support (Outstanding Tier OUT-2):** Supports Indian English (`en-IN`), US English (`en-US`), Hindi (`hi-IN`), and Tamil (`ta-IN`) neural narration.

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       B-ROLL STUDIO SYSTEM ARCHITECTURE                     │
└─────────────────────────────────────────────────────────────────────────────┘

 [Vite React SPA Dashboard]                [CLI Batch Runner / API Clients]
           │                                              │
           └──────────────────────┬───────────────────────┘
                                  │ (HTTP REST /api/v1/)
                                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FASTAPI BACKEND APPLICATION                          │
│                                                                             │
│  - Correlation ID Middleware (X-Correlation-Id)                             │
│  - Idempotency Middleware (Idempotency-Key Header, Conflict = 409)          │
│  - UPPER_SNAKE_CASE Error Formatter ({"error": {"code", ...}})             │
│  - OpenAPI 3.1 Spec (openapi.yaml)                                          │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
         ┌─────────────────────────┼─────────────────────────┐
         ▼                         ▼                         ▼
┌──────────────────┐      ┌──────────────────┐      ┌──────────────────┐
│  Database Layer  │      │  Storage Manager │      │ Background Engine│
│  PostgreSQL 16   │      │  Dual: MinIO S3  │      │ 7-Stage Pipeline │
│  SQLite fallback │      │  Local Dir Store │      │ Celery / Worker  │
└──────────────────┘      └──────────────────┘      └────────┬─────────┘
                                                             │
    ┌────────────────────────────────────────────────────────┴────────┐
    ▼                                                                 ▼
[Adapters & AI Services]                                    [Rendering Engine]
├── TTS: Edge Neural (en-IN, hi-IN, ta-IN)                  ├── FFmpeg & FFprobe
│   └── Offline Deterministic Synthesizer                   ├── Rescale & Crop
├── STT: Silence detection & Acoustic Segmenter             │   (16:9, 9:16, 1:1)
├── Footage Source 1: Curated Commercial Stock              ├── Subtitle Burn-in
├── Footage Source 2: Procedural Generative Engine          ├── Audio AAC Normalise
└── Relevance: Independent VLM Scorer                       └── Concat Demuxer
```

---

## 3. Quick Setup (< 10 Commands)

### Option A: Local Execution (Recommended for Fast Review)

Prerequisites: Python 3.12+ (or 3.13), Node.js 18+, FFmpeg installed on system.

```powershell
# 1. Clone or navigate to repository
cd broll-studio

# 2. Set up virtual environment and install dependencies
python -m venv venv
.\venv\Scripts\pip install -r backend/requirements.txt

# 3. Copy environment configuration
copy .env.example .env

# 4. Run automated test suite (runs 100% offline with NO API keys)
$env:PYTHONPATH="backend"
.\venv\Scripts\pytest backend/tests/ -v

# 5. Start backend application (serves both API and compiled UI)
.\venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000
```
Open your browser at **`http://127.0.0.1:8000/`** to view the production dashboard.

---

### Option B: One-Command Docker Compose

```bash
# Starts API, Worker, PostgreSQL, Redis, MinIO S3, and Frontend
docker compose up -d

# Check health
curl http://localhost:8000/health
```

---

## 4. Automated Testing

Run the full suite of unit, integration, hard cases, and end-to-end rendering tests:

```powershell
$env:PYTHONPATH="backend"
.\venv\Scripts\pytest backend/tests/ -v
```

### Verified Test Summary (22 Passing Tests):
- `test_errors.py`: Standard UPPER_SNAKE_CASE error format.
- `test_scene_planner.py`: Contextual disambiguation (`cloud`, `bank`, `mouse`, `python`, `value`), abstract lines, statistics, safety guardrails.
- `test_footage_selector.py`: Zero-duplicate clip usage, dual-provider routing.
- `test_jobs_api.py`: `GET /health`, `GET /ready`, `POST /api/v1/broll/jobs`, status polling.
- `test_idempotency.py`: Safe retries, identical request caching, conflict detection (409).
- `test_hard_cases.py`: Silent audio rejection, valid audio ingestion, named entities, sensitive news.
- `test_partial_re_render.py`: Clip replacement with measurable render speedup (ADV-2).
- `test_pipeline_e2e.py`: Full video generation verified with `ffprobe` (H.264/AAC, 30fps).

---

## 5. Batch Runner CLI Tool (Integration Standard Point 10)

The batch runner executes a folder of JSON test inputs against the API, polls jobs to completion, and downloads all artifacts into a unified output directory.

```powershell
.\venv\Scripts\python scripts/batch_runner.py --input-dir tests/fixtures/inputs --api-url http://127.0.0.1:8000 --output-dir test_pack
```

### Output Directory Structure (`test_pack/`):
```
test_pack/
  batch_summary.json
  outputs/
    input_01_tutorial/
      video_16_9.mp4
      video_9_16.mp4
      captions.srt
      timeline.json
      manifest.json
    ...
```

---

## 6. API Reference Contract

All application endpoints are served under `/api/v1/`.

### 1. Create a B-Roll Video Job
`POST /api/v1/broll/jobs`  
`Header: Idempotency-Key: <unique-string>`

```json
{
  "script": "Save money automatically every month. Deploying cloud infrastructure protects uptime.",
  "voice": "en-IN-female",
  "aspect_ratios": ["16:9", "9:16"],
  "style": "bright, modern, real-world footage",
  "avoid": ["people's faces"],
  "captions": { "burn_in": true, "srt": true },
  "callback_url": "https://example.com/webhook"
}
```
**Response: `HTTP 202 Accepted`**
```json
{
  "job_id": "4c293c25-454d-4f06-acda-bd228bbb82e4",
  "status": "queued",
  "progress": 0,
  "current_stage": "queued",
  "created_at": "2026-10-20T10:47:00Z",
  "updated_at": "2026-10-20T10:47:00Z"
}
```

### 2. Poll Job Status
`GET /api/v1/jobs/{job_id}`  
Returns current processing stage, 0-100% progress, and artifact links upon completion.

### 3. Retrieve Completed Results
`GET /api/v1/broll/jobs/{job_id}/result`  
Returns complete manifest, timeline, and direct download links for all aspect ratios.

### 4. Swap Scene Clip (Partial Re-render)
`POST /api/v1/broll/jobs/{job_id}/scenes/{scene_index}/swap`
```json
{
  "scene_index": 0,
  "new_clip_id": "stock-work-003",
  "new_visual_hint": "Modern collaborative office"
}
```

---

## 7. Standard Error Structure & Error Codes

Integration Standard Point 5: All errors follow this exact schema:

```json
{
  "error": {
    "code": "UPPER_SNAKE_CASE",
    "message": "Readable explanation of the error",
    "retryable": false,
    "details": {}
  }
}
```

| Error Code | HTTP Status | Meaning |
|---|---|---|
| `VALIDATION_ERROR` | 422 | Request body failed schema validation or missing required fields. |
| `EMPTY_SCRIPT_ERROR` | 400 | Script text is empty or purely whitespace. |
| `UNSUPPORTED_MEDIA_TYPE`| 415 | Uploaded file is not a supported audio format (mp3, wav, m4a). |
| `SILENT_AUDIO_DETECTED` | 400 | Uploaded audio contains only silence or undetectable speech. |
| `AUDIO_DURATION_EXCEEDED`| 400 | Audio exceeds the 10-minute maximum limit. |
| `IDEMPOTENCY_CONFLICT` | 409 | Idempotency-Key reused with a conflicting or different payload. |
| `JOB_NOT_FOUND` | 404 | Target job ID does not exist in the database. |
| `JOB_NOT_READY` | 400 | Attempted to fetch results before job reached `succeeded` status. |
| `SSRF_ATTEMPT_BLOCKED` | 400 | Requested remote URL resolves to a restricted private or loopback IP. |
| `RENDER_ERROR` | 500 | FFmpeg process failed during encoding or filter application. |

---

## 8. Commercial Licensing Compliance

1. **Zero Watermarks:** All footage used in the default pipeline is clean and free of watermarks.
2. **100% Commercial Usability:** Footage is sourced from verified commercial-use stock libraries (Pexels / CC0) or procedurally synthesized by the engine.
3. **No Realistic Living Faces:** The scene planner suppresses realistic face generation when living individuals are named in the script.
4. **Attribution Tracking:** Source URLs, licence URLs, attribution strings, and rights verification status are recorded for every scene in `timeline.json`.
5. **AI Flagging:** Every synthetic procedural clip is tagged with `"is_ai_generated": true`.

---

## 9. Submission Deliverables Index

- `ASSESSMENT_REQUIREMENTS.md`: Numbered checklist mapping all must-haves, levels, and integration points to implementation and test proof.
- `Submission_Form.xlsx`: Formatted 5-tab Excel submission workbook.
- `REPORT.md`: 4-page engineering report detailing architecture, trade-offs, benchmarks, and cost analysis.
- `SOURCES.md`: Complete audit of all libraries, models, and footage sources.
- `AI_USE.md`: Disclosure of AI coding tools and runtime services.
- `SECURITY.md`: Operational security, SSRF defenses, and HMAC callback specifications.
- `TESTING.md`: Reproduction instructions for all test tiers.
- `demo_video_plan.md`: Step-by-step 8-minute demonstration video script.
- `test_pack/`: Full outputs (MP4s, timelines, SRTs, manifests, summary) for all 10 core evaluation inputs.
