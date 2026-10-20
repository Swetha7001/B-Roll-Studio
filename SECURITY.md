# SECURITY.md — Security Architecture, Safeguards & Operational Controls

**Project:** B-Roll Studio — Script & Voiceover Video Engine  
**Assessment:** IncuBrix Engineering Assessment 3  
**Last Updated:** 2026-10-20  

---

## 1. Threat Model & Security Posture

B-Roll Studio processes user-supplied text scripts, remote media URLs, and audio file uploads. Security controls are built into every processing stage.

---

## 2. Server-Side Request Forgery (SSRF) Prevention

When accepting remote audio or footage URLs via `POST /api/v1/broll/jobs` or download adapters:

1. **Protocol Restriction:** Only `http` and `https` schemes are accepted. Protocols such as `file://`, `gopher://`, `ftp://`, or internal UNIX socket paths are blocked immediately with `SSRF_ATTEMPT_BLOCKED`.
2. **DNS & IP Pinning:**
   - Hostnames are resolved to IP addresses via `socket.getaddrinfo`.
   - The resolved IP is inspected using Python's `ipaddress` module.
   - Any connection attempt to private (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopback (`127.0.0.0/8`), link-local (`169.254.0.0/16`), or AWS/cloud metadata services (`169.254.169.254`) is strictly blocked.
3. **Bounded Streaming:** Remote downloads enforce strict size limits (`MAX_FILE_SIZE_MB = 100`) and timeout bounds (`15.0s`), terminating downloads if exceeded.

---

## 3. Webhook Delivery & HMAC-SHA256 Signatures

Integration Standard Point 3 specifies secure asynchronous notifications:

- Outgoing webhook callbacks are signed using **HMAC-SHA256**.
- The signature is calculated over the canonical JSON request body using `settings.WEBHOOK_HMAC_SECRET`.
- The resulting hex digest is delivered in the `X-IncuBrix-Signature` HTTP header.
- Receiving clients verify authenticity by computing the HMAC signature over the raw payload and performing a constant-time comparison.

```python
signature = hmac.new(
    settings.WEBHOOK_HMAC_SECRET.encode("utf-8"),
    payload.encode("utf-8"),
    hashlib.sha256
).hexdigest()
# Header: X-IncuBrix-Signature: <signature>
```

---

## 4. Idempotency & Safe Retries (Integration Standard Point 4)

- The API accepts an `Idempotency-Key` header on all job submission endpoints.
- If a client retries a request with the same `Idempotency-Key` and an identical payload, the existing job is returned without re-executing background rendering.
- If an `Idempotency-Key` is reused with a conflicting or modified payload, the API immediately rejects the request with HTTP 409 `IDEMPOTENCY_CONFLICT`.

---

## 5. Input Validation & Media Sanitization

- **File Extension vs MIME Verification:** File uploads do not rely on user-supplied file extensions. The actual media container and audio streams are probed using `ffprobe`.
- **Duration Limits:** Audio input duration is bounded by `MAX_AUDIO_DURATION_SEC = 600` (10 minutes).
- **Silence & Corrupt Audio Detection:** Zero-duration or undetectable audio streams are rejected with structured `SILENT_AUDIO_DETECTED` errors.
- **Path Traversal Protection:** All storage keys are sanitized using `.lstrip("/\\")` and resolved relative to the configured storage root, preventing directory traversal attacks (`../`).

---

## 6. Secret Hygiene & Zero Hard-Coded Keys

- No API keys, database credentials, or secret tokens are committed to source control.
- Configuration is loaded via environment variables or `.env` files using Pydantic `BaseSettings`.
- A safe `.env.example` provides documentation for all available settings.
- The automated test suite executes 100% offline with zero required paid API keys.
- Application error responses conform to `{"error": {"code", "message", "retryable", "details"}}` and never leak internal stack traces or database connection strings.
