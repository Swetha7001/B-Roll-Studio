# DEMO_VIDEO_PLAN.md — 8-Minute Technical Demonstration Recording Script

**Project:** B-Roll Studio — Script & Voiceover Video Engine  
**Assessment:** IncuBrix Engineering Assessment 3  
**Target Duration:** <= 8 Minutes (Unedited Screen Recording)  
**Last Updated:** 2026-10-20  

---

## 1. Demonstration Checklist & Timeline

| Timestamp | Phase | What to Show on Screen | What to Say / Explain | Acceptance Criteria Verified |
|---|---|---|---|---|
| **0:00 – 1:30** | **System Architecture & Design Decision** | Open VS Code / IDE at `backend/app/services/scene_planner.py` and `backend/app/rendering/partial_renderer.py`. | "Welcome to B-Roll Studio. The core design decision I want to highlight is our **Dual-Provider Routing & Semantic Disambiguation Engine** coupled with **Accelerated Partial Re-rendering**. Instead of naive keyword matching that mistakes 'cloud computing' for weather or 'value' for cash, our engine detects semantic collocations. Furthermore, when a creator replaces a single clip, our partial renderer splices only the affected interval using FFmpeg concat demuxer, achieving a 5x render speedup." | Architecture Explanation (Live Session Part 1 & 4) |
| **1:30 – 3:30** | **Clean Successful Run (Full Pipeline)** | Open Web Dashboard at `http://localhost:8000/`. Click **New Video**. Enter a financial/tech script. Select voices (`en-IN-female`), select 16:9 and 9:16 aspect ratios. Click **Generate Video**. | "Now we submit a clean script. Notice the job transitions from `queued` to `ingesting`, `narrating`, `planning`, `selecting_footage`, and `rendering`. Once completed, we see the synchronized video player in 16:9 and 9:16 portrait. We inspect the timeline: notice how Scene 1 matched currency counting with Pexels commercial license, Scene 2 matched server racks, and Scene 3 generated procedural motion with `is_ai_generated: true`. All clips are 100% licence-clean." | Must-Haves MH-1, MH-2, MH-3, MH-4, MH-5, MH-6 |
| **3:30 – 4:45** | **Partial Re-render (Clip Swap)** | In the completed project view, click **Swap Clip** on Scene 1. Select the collaborative office footage or enter a custom visual hint. Click **Re-render Affected Clip**. | "Notice that instead of re-rendering the entire 1-minute video from scratch, only Scene 1 is transcoded and spliced into the master stream. The system reports: Partial render completed in 3.1s vs full 15.5s (5.0x faster). The manifest and timeline are updated live." | Advanced Tier ADV-2 |
| **4:45 – 6:15** | **Failure Handling & Recovery** | Click **New Video**, select Audio mode, and upload `tests/fixtures/audio/silent.wav` (or enter an empty script `   `). Submit. | "Now let's observe our error recovery. The engine immediately intercepts the silent audio during ffprobe ingestion, marks the job failed, and returns structured JSON: `{"error": {"code": "SILENT_AUDIO_DETECTED", "message": "Uploaded audio contains only silence...", "retryable": false}}`. No crash, no hanging worker, and actionable guidance is displayed." | Must-Have MH-7, Hard Case HC-8, INT-5 |
| **6:15 – 7:30** | **Automated Tests Running** | Switch to terminal. Run: `pytest backend/tests/ -v`. | "Here is our automated test suite running with zero paid API keys: 22 tests passing covering unit error structures, disambiguation, zero-repeat deduplication, idempotency retry safety, hard cases, and an end-to-end video render validated by ffprobe." | Integration Standard Point 1 & Section 14 |
| **7:30 – 8:00** | **Batch Runner & Closing** | Display `test_pack/batch_summary.json` showing 10/10 inputs passed with average relevance 4.5/5.0. | "Finally, our CLI batch runner has executed all 10 core evaluation inputs, downloading videos, timelines, SRTs, and manifests to `test_pack/`. B-Roll Studio is containerised, fully documented, and ready for deployment." | Integration Standard Point 10 |

---

## 2. Pre-Recording Setup Instructions

1. Ensure the backend server is running:
   ```powershell
   Set-Location "C:\Users\USER\.gemini\antigravity\scratch\broll-studio"
   $env:PYTHONPATH="backend"
   .\venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
2. Open Chrome at `http://127.0.0.1:8000/`.
3. Have a terminal window open side-by-side ready to run `pytest backend/tests/ -v`.
4. Keep the recording unedited and under 8 minutes.
