"""Pytest configuration and shared fixtures for unit and integration testing."""
import asyncio
import os
import sys
from pathlib import Path
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

# Ensure backend root is on Python path
sys.path.insert(0, str(Path(__file__).parent.parent.resolve()))

# Use isolated test database so pytest never drops development database tables
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_broll_studio.db"

from app.core.config import settings
from app.core.database import AsyncSessionLocal, Base, engine, get_db
from app.models.job import Job, JobArtifact, Scene  # noqa: F401
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_db():
    """Sets up a clean test database schema per test."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_client(test_db):
    """Provides async HTTP client connected directly to the FastAPI ASGI app."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
