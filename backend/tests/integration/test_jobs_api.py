"""Integration tests for Job Lifecycle API."""
import pytest


@pytest.mark.asyncio
async def test_health_and_ready_endpoints(async_client):
    health = await async_client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    ready = await async_client.get("/ready")
    assert ready.status_code in (200, 503)
    assert "checks" in ready.json()


@pytest.mark.asyncio
async def test_create_and_poll_job(async_client):
    payload = {
        "script": "Testing automated background job lifecycle.",
        "voice": "en-IN-female",
        "aspect_ratios": ["16:9"]
    }
    create_resp = await async_client.post("/api/v1/broll/jobs", json=payload)
    assert create_resp.status_code == 202
    job_data = create_resp.json()
    job_id = job_data["job_id"]
    assert job_data["status"] in ("queued", "running")

    # Poll status
    status_resp = await async_client.get(f"/api/v1/jobs/{job_id}")
    assert status_resp.status_code == 200
    st_data = status_resp.json()
    assert st_data["job_id"] == job_id
    assert "progress" in st_data


@pytest.mark.asyncio
async def test_invalid_empty_input_rejection(async_client):
    payload = {
        "script": "   ",
        "voice": "en-IN-female"
    }
    resp = await async_client.post("/api/v1/broll/jobs", json=payload)
    assert resp.status_code in (400, 422)
    err = resp.json()
    assert err["error"]["code"] in ("VALIDATION_ERROR", "EMPTY_SCRIPT_ERROR")
