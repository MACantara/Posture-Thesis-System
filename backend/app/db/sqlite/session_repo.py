import aiosqlite

from app.db.interfaces import Session, SessionRepository
from app.config import settings


class SqliteSessionRepository(SessionRepository):
    def __init__(self, db_path=None):
        self._db_path = str(db_path) if db_path else str(settings.db_path)

    async def start_session(self, user_id: int) -> int:
        async with aiosqlite.connect(self._db_path) as db:
            cursor = await db.execute(
                "INSERT INTO sessions (user_id) VALUES (?)",
                (user_id,),
            )
            await db.commit()
            return cursor.lastrowid

    async def end_session(self, session_id: int, good_count: int = 0,
                          warning_count: int = 0, poor_count: int = 0,
                          avg_angle: float | None = None) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """UPDATE sessions
                   SET end_time = CURRENT_TIMESTAMP,
                       good_count = ?, warning_count = ?, poor_count = ?, avg_angle = ?
                   WHERE id = ?""",
                (good_count, warning_count, poor_count, avg_angle, session_id),
            )
            await db.commit()

    async def get_by_user(self, user_id: int) -> list[Session]:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT * FROM sessions WHERE user_id = ? ORDER BY start_time DESC",
                (user_id,),
            )
            rows = await cursor.fetchall()
            return [
                Session(
                    id=row["id"],
                    user_id=row["user_id"],
                    start_time=row["start_time"],
                    end_time=row["end_time"],
                    good_count=row["good_count"],
                    warning_count=row["warning_count"],
                    poor_count=row["poor_count"],
                    avg_angle=row["avg_angle"],
                )
                for row in rows
            ]
