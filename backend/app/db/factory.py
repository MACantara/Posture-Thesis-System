from dataclasses import dataclass

from app.config import settings
from app.db.interfaces import PostureRepository, SessionRepository, UserRepository
from app.db.sqlite.posture_repo import SqlitePostureRepository
from app.db.sqlite.session_repo import SqliteSessionRepository
from app.db.sqlite.user_repo import SqliteUserRepository
from app.db.postgresql.posture_repo import PostgresPostureRepository
from app.db.postgresql.session_repo import PostgresSessionRepository
from app.db.postgresql.user_repo import PostgresUserRepository


@dataclass
class Repositories:
    users: UserRepository
    posture: PostureRepository
    sessions: SessionRepository


def get_repositories() -> Repositories:
    backend = settings.DB_BACKEND

    if backend == "sqlite":
        return Repositories(
            users=SqliteUserRepository(),
            posture=SqlitePostureRepository(),
            sessions=SqliteSessionRepository(),
        )
    elif backend == "postgresql":
        return Repositories(
            users=PostgresUserRepository(),
            posture=PostgresPostureRepository(),
            sessions=PostgresSessionRepository(),
        )
    elif backend == "supabase":
        raise NotImplementedError("Supabase backend not yet implemented. Use DB_BACKEND=sqlite or postgresql.")
    else:
        raise ValueError(f"Unknown DB_BACKEND: {backend}")
