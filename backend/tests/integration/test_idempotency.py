"""Integration tests for Idempotency and Safe Retries (Integration Standard Point 4)."""
import pytest


@pytest.mark.asyncio
async def test_idempotent_identical_submission(async_client):
    payload = {
        "script": "Building software with automated testing ensures system stability.",
        "voice": "en-IN-female",
        "aspect_ratios": ["16:9"]
    }
    headers = {"Idempotency-Key": "test-key-001"}

    # First request
    resp1 = await async_client.post("/api/v1/broll/jobs", json=payload, headers=headers)
    assert resp1.status_code == 202
    data1 = resp1.json()
    job_id1 = data1["job_id"]

    # Identical retry
    resp2 = await async_client.post("/api/v1/broll/jobs", json=payload, headers=headers)
    assert resp2.status_code == 202
    data2 = resp2.json()
    assert data2["job_id"] == job_id1, "Idempotent retry must return the exact same job ID"


@pytest.mark.asyncio
async def test_idempotent_conflicting_payload(async_client):
    headers = {"Idempotency-Key": "test-key-conflict-002"}

    payload1 = {
        "script": "Initial version of the script.",
        "voice": "en-IN-female"
    }
    resp1 = await async_client.post("/api/v1/broll/jobs", json=payload1, headers=headers)
    assert resp1.status_code == 202

    # Conflicting payload with same idempotency key
    payload2 = {
        "script": "Conflicting different text for the script.",
        "voice": "en-IN-female"
    }
    resp2 = await async_client.post("/api/v1/broll/jobs", json=payload2, headers=headers)
    assert resp2.status_code == 409
    err = resp2.json()
    assert err["error"]["code"] == "IDEMPOTENCY_CONFLICT"
