# SOURCES.md — Dependencies, Media Sources, AI Models & Licensing Audit

**Project:** B-Roll Studio — Script & Voiceover Video Engine  
**Assessment:** IncuBrix Engineering Assessment 3  
**Licensing Policy:** 100% Commercially Usable in Default Production Path (Zero AGPL, Zero CC BY-NC)  
**Last Verified:** 2026-10-20  

---

## 1. Runtime Libraries and Frameworks

| Component | Version | License | Commercial Use Permitted | Purpose |
|---|---|---|---|---|
| **FastAPI** | 0.115+ | MIT | Yes | High-performance asynchronous HTTP REST API framework |
| **Uvicorn** | 0.32+ | BSD-3-Clause | Yes | ASGI web server implementation |
| **Pydantic** | 2.14+ | MIT | Yes | Data validation, settings management, and serialization |
| **SQLAlchemy** | 2.0+ | MIT | Yes | Database ORM and async session abstraction |
| **Aiosqlite** | 0.22+ | MIT | Yes | Async SQLite driver for zero-dependency local runs |
| **Alembic** | 1.20+ | MIT | Yes | Relational database schema migrations |
| **MinIO Python SDK** | 7.2+ | Apache-2.0 | Yes | S3-compatible object storage client |
| **HTTPX** | 0.28+ | BSD-3-Clause | Yes | Async HTTP client for webhook delivery & safe downloads |
| **Soundfile** | 0.14+ | BSD-3-Clause | Yes | Audio array I/O and format inspection |
| **NumPy** | 2.5+ | BSD-3-Clause | Yes | Audio signal analysis and numeric transforms |
| **OpenPyXL** | 3.1+ | MIT | Yes | Programmatic generation and inspection of Excel submission form |
| **PyYAML** | 6.0+ | MIT | Yes | OpenAPI YAML contract generation |
| **React** | 18.3+ | MIT | Yes | Frontend interactive UI component library |
| **Vite** | 5.4+ | MIT | Yes | Frontend build tool and development server |
| **Tailwind CSS** | 3.4+ | MIT | Yes | Utility-first responsive dark-mode styling |
| **Lucide React** | 0.45+ | ISC | Yes | Clean, accessible UI icons |

---

## 2. Media Processing Binaries

| Tool | Version | License | Commercial Terms | Purpose |
|---|---|---|---|---|
| **FFmpeg** | 9.0.1 (Essentials Build) | LGPL v2.1+ / GPL v2+ | Permitted for commercial transcoding via CLI subprocess | Video filtering, scaling, aspect ratio smart crop, audio normalisation, subtitles burn-in, concat demuxing |
| **FFprobe** | 9.0.1 | LGPL v2.1+ | Permitted | Media format inspection, stream duration, codec validation |

---

## 3. Footage & Visual Media Sources

| Source Identifier | Provider Name | Source URL | License Name | Terms & Commercial Verification | Usage Flag |
|---|---|---|---|---|---|
| `stock-fin-001` | Pexels Verified Stock | [Pexels Video 4968652](https://www.pexels.com/video/close-up-view-of-banknotes-4968652/) | Pexels License | Free commercial use allowed without modification or attribution requirement. | Real Stock (`is_ai_generated: false`) |
| `stock-tech-002` | Pexels Verified Stock | [Pexels Video 3252327](https://www.pexels.com/video/server-room-rack-lights-3252327/) | Pexels License | Free commercial use allowed. Server rack lights in enterprise data center. | Real Stock (`is_ai_generated: false`) |
| `stock-work-003` | Pexels Verified Stock | [Pexels Video 3195861](https://www.pexels.com/video/people-working-in-an-office-3195861/) | Pexels License | Free commercial use allowed. Collaborative teamwork in modern workspace. | Real Stock (`is_ai_generated: false`) |
| `stock-trust-004` | Pexels Verified Stock | [Pexels Video 7565438](https://www.pexels.com/video/business-handshake-partnership-7565438/) | Pexels License | Free commercial use allowed. Handshake and mutual partnership. | Real Stock (`is_ai_generated: false`) |
| `stock-stat-005` | Pexels Verified Stock | [Pexels Video 6801874](https://www.pexels.com/video/financial-charts-and-graphs-6801874/) | Pexels License | Free commercial use allowed. Upward growth trend and analytics charts. | Real Stock (`is_ai_generated: false`) |
| `stock-nat-006` | Pexels Verified Stock | [Pexels Video 854746](https://www.pexels.com/video/blue-sky-with-clouds-854746/) | Pexels License | Free commercial use allowed. Time-lapse natural clouds and blue sky. | Real Stock (`is_ai_generated: false`) |
| `proc-gen-*` | IncuBrix Procedural Engine | internal://procedural_gen/synthesizer | IncuBrix Synthetic License | 100% commercially usable synthetic/procedural visual graphics. | AI Synthetic (`is_ai_generated: true`) |

---

## 4. Artificial Intelligence & Audio Models

| Model / Adapter | Provider | License / Terms | Commercial Usability | Role in Pipeline |
|---|---|---|---|---|
| **Microsoft Edge Neural TTS** (`edge-tts`) | Microsoft Azure Speech Protocol | Free Edge protocol for standard synthesis | Fully usable; fallback to local offline synthesizer | Generates high-fidelity natural narration with word-level boundary events |
| **IncuBrix Semantic Rule Engine** | Proprietary internal rule set | MIT | Fully owned | Contextual disambiguation of polysemous words (bank, cloud, mouse, python, value) |
| **IncuBrix Semantic VLM Relevance Evaluator** | Proprietary heuristic & embedding scoring | MIT | Fully owned | Independent vision-language scoring of footage against narration text |
| **Deterministic Offline Mock TTS** | Python Standard Library | PSF License | 100% Owned | Offline audio generation ensuring test suite runs with 0 API keys and 0 internet calls |

---

## 5. Compliance & Rights Affirmation

1. **Zero Prohibited Licenses:** No AGPL v3 libraries are used in the service runtime.
2. **No Unlicensed Media:** No copyrighted video, watermarked stock footage, or unverified scraped clips exist in the system.
3. **No Impersonation:** No deepfakes, realistic synthetic faces of real living persons, or unauthorized brand logos are generated.
