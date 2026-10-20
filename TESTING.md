# TESTING.md — Automated Test Suite & Quality Assurance Guide

**Project:** B-Roll Studio — Script & Voiceover Video Engine  
**Assessment:** IncuBrix Engineering Assessment 3  
**Pass Target:** 100% Core Tests Passing Without External API Keys  
**Last Verified:** 2026-10-20  

---

## 1. Quality Philosophy

IncuBrix Assessment 3 requires that:
- Every must-have and integration point has verifiable automated tests.
- Automated tests run **100% offline with zero paid API keys**.
- Rendered video outputs are inspected using `ffprobe` to verify codecs, framerate, pixel formats, and audio synchronization.

---

## 2. Test Execution Command

From the repository root:

```powershell
# Windows
$env:PYTHONPATH="backend"
.\venv\Scripts\pytest backend/tests/ -v

# Linux / macOS / Docker
export PYTHONPATH=backend
pytest backend/tests/ -v
```

---

## 3. Test Suite Breakdown

### A. Unit Tests (`backend/tests/unit/`)
1. **`test_errors.py`:**
   - Verifies the standard JSON error schema: `{"error": {"code", "message", "retryable", "details"}}`.
   - Confirms all error codes use `UPPER_SNAKE_CASE` (Integration Standard Point 5).
2. **`test_scene_planner.py`:**
   - Tests contextual disambiguation of double-meaning words:
     - `cloud` (tech servers vs weather sky)
     - `bank` (financial savings vs river bank)
     - `python` (software development vs reptile)
     - `value` (ethical integrity & trust vs currency asset valuation)
   - Tests abstract line metaphors ("trust is earned slowly" -> craftsman & foundations).
   - Tests statistics lines ("sales grew 40% in 2025" -> analytics charts).
   - Tests safety guardrails: detection of named people (Elon Musk) and brands (Apple, Google).
   - Tests structured IncuBrix scene lists (`[{"text": "...", "visual_hint": "..."}]`).
3. **`test_footage_selector.py`:**
   - Verifies dual-provider routing rules:
     - Concrete physical topics -> Curated Commercial Stock (`curated_stock`).
     - Abstract conceptual topics -> Procedural Motion Engine (`procedural_gen`).
   - Verifies **ZERO duplicate clips** across all scenes within a single video (Must-Have MH-5).
   - Verifies independent relevance scoring.

### B. Integration Tests (`backend/tests/integration/`)
1. **`test_jobs_api.py`:**
   - Verifies `GET /health` and `GET /ready` (Integration Standard Point 8).
   - Verifies `POST /api/v1/broll/jobs` returns HTTP 202 with `job_id` and initial status `queued` (Integration Standard Point 3).
   - Verifies status polling at `GET /api/v1/jobs/{job_id}` with 0-100 progress tracking.
   - Verifies empty script rejection with HTTP 400/422.
2. **`test_idempotency.py`:**
   - Verifies `Idempotency-Key` header prevents duplicate background rendering for identical retries.
   - Verifies `IDEMPOTENCY_CONFLICT` (HTTP 409) when an idempotency key is reused with conflicting parameters.
3. **`test_hard_cases.py`:**
   - Tests silent audio input rejection (`SILENT_AUDIO_DETECTED`).
   - Tests valid audio input ingestion (`sample_voiceover.wav`).
   - Tests sensitive/sad news handling.
4. **`test_partial_re_render.py`:**
   - Verifies Advanced Requirement ADV-2: clip swap on a single scene triggers an accelerated partial re-render.
   - Measures and proves partial render duration is measurably faster than full render.

### C. End-to-End Pipeline Test (`backend/tests/e2e/test_pipeline_e2e.py`)
- Full execution: Ingestion -> Narration audio generation -> Scene planning -> Dual-source clip matching -> Multi-aspect rendering (16:9 and 9:16) -> Subtitle burn-in -> SRT generation -> `timeline.json` -> `manifest.json`.
- Uses `ffprobe` to verify:
  - Video stream: H.264 (`h264`), 1920x1080, 30 fps.
  - Audio stream: AAC (`aac`), stereo, 48kHz, 192kbps.
  - Duration > 1.0s and strictly matches narration duration (no black frames, frozen frames, or audio drift).

---

## 4. Batch Runner Reproduction

Run the automated batch test against the 10 varied inputs:

```powershell
.\venv\Scripts\python scripts/batch_runner.py --input-dir tests/fixtures/inputs --api-url http://127.0.0.1:8000 --output-dir test_pack
```

Results are saved to `test_pack/batch_summary.json` and `test_pack/outputs/<input_id>/`.

---

## 5. Frontend Production Build Verification

Verify that the frontend builds with zero TypeScript errors:

```powershell
cd frontend
npm run build
```
Outputs static assets into `frontend/dist/`.
