import pytest
import asyncio
import os

from app.db.sqlite.connection import init_db
from app.db.sqlite.user_repo import SqliteUserRepository
from app.db.sqlite.posture_repo import SqlitePostureRepository
from app.db.sqlite.session_repo import SqliteSessionRepository
from app.db.factory import Repositories
from app.auth.password import hash_password


@pytest.mark.asyncio
async def test_seed_creates_users(tmp_path):
    db_path = tmp_path / "seed_test.db"
    await init_db(db_path)

    repos = Repositories(
        users=SqliteUserRepository(db_path),
        posture=SqlitePostureRepository(db_path),
        sessions=SqliteSessionRepository(db_path),
    )

    await repos.users.create("user", hash_password("pass123"), "user", "Manila")
    await repos.users.create("admin", hash_password("admin123"), "admin", "Quezon City")

    users = await repos.users.list_all()
    assert len(users) == 2
    assert any(u.username == "user" for u in users)
    assert any(u.username == "admin" for u in users)


@pytest.mark.asyncio
async def test_seed_creates_posture_records(tmp_path):
    db_path = tmp_path / "seed_test.db"
    await init_db(db_path)

    repos = Repositories(
        users=SqliteUserRepository(db_path),
        posture=SqlitePostureRepository(db_path),
        sessions=SqliteSessionRepository(db_path),
    )

    user = await repos.users.create("testuser", hash_password("pass"), "user", "Manila")
    session_id = await repos.sessions.start_session(user.id)

    await repos.posture.insert(user.id, "good", 5.0, 10.0, session_id)
    await repos.posture.insert(user.id, "warning", 15.0, 8.0, session_id)
    await repos.posture.insert(user.id, "poor", 30.0, 5.0, session_id)

    records = await repos.posture.get_by_user(user.id)
    assert len(records) == 3

    stats = await repos.posture.get_stats(user.id)
    assert stats.good_posture_count == 1
