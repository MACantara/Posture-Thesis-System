import asyncio
import os
import tempfile
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Set test environment variables before importing app
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DB_BACKEND"] = "sqlite"

from app.db.sqlite.connection import init_db, get_connection
from app.db.sqlite.user_repo import SqliteUserRepository
from app.db.sqlite.posture_repo import SqlitePostureRepository
from app.db.sqlite.session_repo import SqliteSessionRepository
from app.db.factory import Repositories
from app.auth.password import hash_password


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    return tmp_path / "test_posture.db"


@pytest_asyncio.fixture
async def app_instance(temp_db_path: Path):
    await init_db(temp_db_path)

    # Create repos with explicit db_path
    repos = Repositories(
        users=SqliteUserRepository(temp_db_path),
        posture=SqlitePostureRepository(temp_db_path),
        sessions=SqliteSessionRepository(temp_db_path),
    )

    # Seed test users
    await repos.users.create("user", hash_password("pass123"), "user", "Manila")
    await repos.users.create("admin", hash_password("admin123"), "admin", "Quezon City")

    from app.main import app
    app.state.repos = repos
    yield app


@pytest_asyncio.fixture
async def client(app_instance):
    transport = ASGITransport(app=app_instance)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def user_token(client):
    response = await client.post("/api/auth/login", json={
        "username": "user",
        "password": "pass123",
    })
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def admin_token(client):
    response = await client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123",
    })
    return response.json()["access_token"]


@pytest_asyncio.fixture
async def auth_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}


@pytest_asyncio.fixture
async def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
