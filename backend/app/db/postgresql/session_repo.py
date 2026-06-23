import asyncpg

from app.db.interfaces import Session, SessionRepository
from app.db.postgresql.connection import get_connection, release_connection


class PostgresSessionRepository(SessionRepository):
    async def start_session(self, user_id: int) -> int:
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                "INSERT INTO sessions (user_id) VALUES ($1) RETURNING id",
                user_id,
            )
            return row["id"]
        finally:
            await release_connection(conn)

    async def end_session(self, session_id: int, good_count: int = 0,
                          warning_count: int = 0, poor_count: int = 0,
                          avg_angle: float | None = None) -> None:
        conn = await get_connection()
        try:
            await conn.execute(
                """UPDATE sessions
                   SET end_time = CURRENT_TIMESTAMP,
                       good_count = $1, warning_count = $2, poor_count = $3, avg_angle = $4
                   WHERE id = $5""",
                good_count, warning_count, poor_count, avg_angle, session_id,
            )
        finally:
            await release_connection(conn)

    async def get_by_user(self, user_id: int) -> list[Session]:
        conn = await get_connection()
        try:
            rows = await conn.fetch(
                "SELECT * FROM sessions WHERE user_id = $1 ORDER BY start_time DESC",
                user_id,
            )
            return [
                Session(
                    id=row["id"],
                    user_id=row["user_id"],
                    start_time=row["start_time"].isoformat() if row["start_time"] else None,
                    end_time=row["end_time"].isoformat() if row["end_time"] else None,
                    good_count=row["good_count"],
                    warning_count=row["warning_count"],
                    poor_count=row["poor_count"],
                    avg_angle=row["avg_angle"],
                )
                for row in rows
            ]
        finally:
            await release_connection(conn)
