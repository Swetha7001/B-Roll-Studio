# ASSESSMENT_REQUIREMENTS.md — IncuBrix Engineering Assessment 3 Verification Matrix

**Project:** B-Roll Studio — Script & Voiceover Video Engine  
**Assessment:** IncuBrix Engineering Assessment 3 (Script and Voiceover to B-roll Video Engine)  
**Evaluator Target:** 85+ / 100 (Top Pick - Hire)  
**Last Updated:** 2026-10-20  

---

## 1. Must-Haves (Pass / Fail — All 8 Must Pass)

| # | Must-Have Requirement | Implementation Location | Test Verification | Evidence / Artifact | Status |
|---|----------------------|-------------------------|-------------------|---------------------|--------|
| **MH-1** | **Both Inputs Work**: Audio (mp3, wav, m4a, up to 10 min) and text (generates narration via TTS) | `backend/app/services/ingestion.py`, `backend/app/adapters/tts/` | `tests/unit/test_ingestion.py`, `tests/integration/test_pipeline_e2e.py` | Audio probe reports, generated narration `.wav` files, audio transcript | IN_PROGRESS |
| **MH-2** | **Scenes by Meaning & Timed to Voice**: Boundaries align to sentences/phrases; 100% narration covered; narration sets timing | `backend/app/services/scene_planner.py`, `backend/app/rendering/timeline.py` | `tests/unit/test_scene_planner.py`, `tests/integration/test_timeline.py` | `timeline.json` coverage metrics, start/end timestamps matching audio duration | IN_PROGRESS |
| **MH-3** | **Every Clip is Licence-Clean**: Source, licence, attribution, link per clip; 100% commercial use allowed; no watermarks; AI clips flagged | `backend/app/adapters/footage/`, `backend/app/core/licensing.py` | `tests/unit/test_licensing.py`, `tests/integration/test_footage_selection.py` | `timeline.json` licence fields, `SOURCES.md`, rights verification table | IN_PROGRESS |
| **MH-4** | **Correct, Consistent Video**: Output for all requested aspect ratios (16:9, 9:16, 1:1); normalised resolution, 30 fps, pixel format; no black/frozen frames or audio drift | `backend/app/rendering/ffmpeg_engine.py` | `tests/unit/test_ffmpeg_engine.py`, `tests/e2e/test_render_integrity.py` | ffprobe JSON inspection on rendered `video_*.mp4`, zero audio drift logs | IN_PROGRESS |
| **MH-5** | **No Repeats & No Nonsense Matches**: No clip used twice in one video; semantic matching over raw keyword matching | `backend/app/services/footage_selector.py` | `tests/unit/test_footage_selector.py`, `tests/integration/test_relevance.py` | Clip deduplication assertion in test suite, relevance scores > 3.5 | IN_PROGRESS |
| **MH-6** | **Safe Output**: No realistic faces of real people; no invented brand logos; respectful imagery for sensitive/sad news | `backend/app/services/safety_filter.py` | `tests/unit/test_safety_filter.py`, `tests/integration/test_hard_cases.py` | Safety inspection audit log, test cases covering named entities and sad news | IN_PROGRESS |
| **MH-7** | **Resilient Jobs**: Real background processing with progress tracking; auto-fallback when footage provider fails | `backend/app/workers/job_runner.py`, `backend/app/adapters/footage/` | `tests/integration/test_resilience.py` | Job status progression logs (0->100%), fallback activation events in manifest | IN_PROGRESS |
| **MH-8** | **Integration Standard Followed**: All 10 points implemented; reproducible local start and test | Complete repository architecture & `docker-compose.yml` | `scripts/test_integration.py`, automated test runner | Verified Integration Checklist in Section 3 | IN_PROGRESS |

---

## 2. Assessment Levels (40 Marks: Core 15 + Advanced 15 + Outstanding 10)

### A. Core Level (15 Marks)
- [ ] **CORE-1**: All 8 Must-haves pass unconditionally.
- [ ] **CORE-2**: 10 varied inputs (tutorial, news summary, product promo, short story, abstract narration, financial stats, ambiguous words, accents, varying lengths 20s to 5min) all produce usable videos.
- [ ] **CORE-3**: Average relevance >= 3.5 / 5.0 across all 10 test videos.

### B. Advanced Level (15 Marks)
- [ ] **ADV-1**: At least two footage sources (e.g., Curated Commercial Stock footage and Generative/Procedural synthesis) with written, measurable selection rule stored in `timeline.json`.
- [ ] **ADV-2**: **Swap a Clip**: User can replace a single scene's clip and trigger partial re-render of only the affected interval in measurably less time than full render.
- [ ] **ADV-3**: **Visual Cohesion**: Normalised colour and brightness curves; sensible pacing with no 0.5s strobing or flash-cuts.
- [ ] **ADV-4**: Accepts IncuBrix structured scene lists: `[{"text": "...", "visual_hint": "..."}]`.

### C. Outstanding Level (10 Marks)
- [ ] **OUT-1**: **Independent Relevance Scoring**: Vision-language model / semantic embedding scoring each clip against narration; correlation matrix against human ratings.
- [ ] **OUT-2**: **Multilingual Support**: Hindi (`hi-IN`) and Tamil (`ta-IN`) voiceovers, transcription, and scene semantic handling.
- [ ] **OUT-3**: **Production Numbers**: Measured time and cost per minute of finished video; server concurrency benchmark.
- [ ] **OUT-4**: At least 85% of scenes rated 4 or 5 out of 5 by evaluation rubric.

---

## 3. Integration Standard Checklist (20 Marks — 2 Marks Each)

| # | Integration Requirement | Implementation Details | Verification Test | Status |
|---|------------------------|------------------------|-------------------|--------|
| **INT-1** | **One-command start and test** | `docker-compose.yml`, root `Makefile`/scripts, `.env.example` with zero mandatory paid keys | `python scripts/batch_runner.py --self-test`, `pytest` | IN_PROGRESS |
| **INT-2** | **Documented HTTP API** | `openapi.yaml` (OpenAPI 3.1) matching FastAPI routes under `/api/v1/` | `tests/unit/test_openapi_spec.py` | IN_PROGRESS |
| **INT-3** | **Background Jobs** | POST returns HTTP 202 with `job_id`; `GET /api/v1/jobs/{job_id}` returns status/progress/results; HMAC-SHA256 signed callbacks | `tests/integration/test_jobs_api.py` | IN_PROGRESS |
| **INT-4** | **Safe Retries** | `Idempotency-Key` header on POST endpoints; duplicate requests return identical job without duplicate work | `tests/integration/test_idempotency.py` | IN_PROGRESS |
| **INT-5** | **Clear Errors** | Structured JSON: `{"error": {"code": "...", "message": "...", "retryable": bool, "details": {}}}` with UPPER_SNAKE_CASE codes | `tests/unit/test_errors.py` | IN_PROGRESS |
| **INT-6** | **Configuration** | Pydantic `BaseSettings` reading from `.env` and environment variables; zero hard-coded paths or credentials | `tests/unit/test_config.py` | IN_PROGRESS |
| **INT-7** | **Files In, Files Out** | File uploads (multipart) and URLs supported; MinIO / S3 object storage; verified download links | `tests/integration/test_storage.py` | IN_PROGRESS |
| **INT-8** | **Logs and Health** | Structured JSON logs with timestamp, level, `job_id`, `correlation_id`; `GET /health` and `GET /ready` endpoints | `tests/unit/test_observability.py` | IN_PROGRESS |
| **INT-9** | **Output Manifest** | Comprehensive `manifest.json` per job detailing models, versions, timings, settings, cost estimate, and licence information | `tests/unit/test_manifest.py` | IN_PROGRESS |
| **INT-10** | **Batch Runner** | CLI utility (`scripts/batch_runner.py`) running folder of test inputs, polling to completion, outputting structured folder | `tests/e2e/test_batch_runner.py` | IN_PROGRESS |

---

## 4. Hard Cases Verification Matrix

| Case ID | Scenario | Expected System Behaviour | Test Fixture | Status |
|---------|----------|---------------------------|--------------|--------|
| **HC-1** | Abstract lines ("trust is earned slowly") | Contextual metaphors (e.g., craftsmen, foundations, handshake), avoidance of literal nonsense | `tests/fixtures/inputs/01_abstract.json` | IN_PROGRESS |
| **HC-2** | Statistics ("sales grew 40% in 2025") | Growth charts, analytics dashboard, upward visual trends | `tests/fixtures/inputs/02_statistics.json` | IN_PROGRESS |
| **HC-3** | Named person / brand mentioned | Neutral, respectful illustrative B-roll (no fake AI likeness or copyright infringements) | `tests/fixtures/inputs/03_named_brand.json` | IN_PROGRESS |
| **HC-4** | Double meanings ("cloud", "bank", "mouse") | Disambiguation based on sentence context (tech cloud vs weather; river bank vs finance) | `tests/fixtures/inputs/04_disambiguation.json` | IN_PROGRESS |
| **HC-5** | Sad / sensitive news story | Somber, respectful footage; warning flag; no sensationalized or inappropriate clips | `tests/fixtures/inputs/05_sensitive_news.json` | IN_PROGRESS |
| **HC-6** | 9:16 portrait output from 16:9 source | Intelligent smart crop / center weighting preserving subject without distortion | `tests/fixtures/inputs/06_portrait_crop.json` | IN_PROGRESS |
| **HC-7** | Long voiceover (5 minutes) | Robust chunking, stable memory usage, no audio drift | `tests/fixtures/inputs/07_long_5min.json` | IN_PROGRESS |
| **HC-8** | Silent or music-only audio | Rejection or explicit warning: `INVALID_AUDIO_CONTENT` with actionable guidance | `tests/fixtures/audio/silent.wav` | IN_PROGRESS |
| **HC-9** | Unsupported file format / empty script | Immediate 400/422 validation error with structured schema | `tests/fixtures/inputs/invalid_empty.json` | IN_PROGRESS |
| **HC-10** | Provider downtime / corrupted clip | Seamless fallback to secondary provider or procedural asset; zero job failure | Mock provider timeout test | IN_PROGRESS |
| **HC-11** | Concurrent submissions | Multi-worker queue safety, zero cross-talk, independent storage keys | `tests/integration/test_concurrency.py` | IN_PROGRESS |

---

## 5. Required Deliverable Artifacts

- [ ] `ASSESSMENT_REQUIREMENTS.md` (this file)
- [ ] `Submission_Form.xlsx` / `Submission_Form.csv` populated with honest verified data
- [ ] `README.md` with complete architecture diagram, setup in < 10 commands, troubleshooting
- [ ] `openapi.yaml` OpenAPI 3.1 specification matching implementation
- [ ] `REPORT.md` (2–4 page technical report covering architecture, decisions, metrics, cost)
- [ ] `SOURCES.md` (all libraries, APIs, footage sources, licenses)
- [ ] `AI_USE.md` (truthful disclosure of AI coding assistants and runtime models)
- [ ] `SECURITY.md` (SSRF protections, auth, HMAC callback signatures, secret hygiene)
- [ ] `TESTING.md` (test reproduction guide, unit/integration/e2e instructions)
- [ ] `test_pack/` (10 core test inputs, full outputs, logs, diagnostics index)
- [ ] `demo_video_plan.md` (minute-by-minute 8-minute live demo checklist)
