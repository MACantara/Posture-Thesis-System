import aiosqlite

from app.db.interfaces import PostureRecord, PostureRepository, PostureStats
from app.config import settings


class SqlitePostureRepository(PostureRepository):
    def __init__(self, db_path=None):
        self._db_path = str(db_path) if db_path else str(settings.db_path)

    async def insert(self, user_id: int, status: str, angle: float,
                     duration: float | None = None, session_id: int | None = None,
                     notes: str | None = None) -> PostureRecord:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """INSERT INTO posture_records (user_id, session_id, status, angle, duration, notes)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (user_id, session_id, status, angle, duration, notes),
            )
            await db.commit()
            record_id = cursor.lastrowid
            cursor = await db.execute("SELECT * FROM posture_records WHERE id = ?", (record_id,))
            row = await cursor.fetchone()
            return PostureRecord(
                id=row["id"],
                user_id=row["user_id"],
                session_id=row["session_id"],
                timestamp=row["timestamp"],
                status=row["status"],
                angle=row["angle"],
                duration=row["duration"],
                notes=row["notes"],
            )

    async def get_by_user(self, user_id: int, status_filter: str | None = None,
                          limit: int = 50, offset: int = 0) -> list[PostureRecord]:
        query = "SELECT * FROM posture_records WHERE user_id = ?"
        params: list = [user_id]
        if status_filter and status_filter != "all":
            query += " AND status = ?"
            params.append(status_filter)
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            return [
                PostureRecord(
                    id=row["id"],
                    user_id=row["user_id"],
                    session_id=row["session_id"],
                    timestamp=row["timestamp"],
                    status=row["status"],
                    angle=row["angle"],
                    duration=row["duration"],
                    notes=row["notes"],
                )
                for row in rows
            ]

    async def get_stats(self, user_id: int) -> PostureStats:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT COUNT(*) as total FROM sessions WHERE user_id = ?", (user_id,)
            )
            row = await cursor.fetchone()
            total_sessions = row["total"]

            cursor = await db.execute(
                "SELECT COUNT(*) as count FROM posture_records WHERE user_id = ? AND status = 'good'",
                (user_id,),
            )
            row = await cursor.fetchone()
            good_count = row["count"]

            cursor = await db.execute(
                "SELECT AVG(angle) as avg_angle FROM posture_records WHERE user_id = ?",
                (user_id,),
            )
            row = await cursor.fetchone()
            avg_angle = row["avg_angle"] if row["avg_angle"] is not None else 0.0

            cursor = await db.execute(
                """SELECT
                    CAST(SUM(CASE WHEN status = 'good' THEN 1 ELSE 0 END) AS FLOAT)
                    / NULLIF(COUNT(*), 0) as rate
                   FROM posture_records WHERE user_id = ?""",
                (user_id,),
            )
            row = await cursor.fetchone()
            current_rate = row["rate"] if row["rate"] is not None else 0.0

            cursor = await db.execute(
                """SELECT
                    CAST(SUM(CASE WHEN status = 'good' THEN 1 ELSE 0 END) AS FLOAT)
                    / NULLIF(COUNT(*), 0) as rate
                   FROM posture_records
                   WHERE user_id = ? AND timestamp >= date('now', '-7 days')""",
                (user_id,),
            )
            row = await cursor.fetchone()
            recent_rate = row["rate"] if row["rate"] is not None else 0.0

            improvement_rate = recent_rate - current_rate

            return PostureStats(
                total_sessions=total_sessions,
                good_posture_count=good_count,
                average_angle=round(avg_angle, 2),
                improvement_rate=round(improvement_rate, 2),
            )
