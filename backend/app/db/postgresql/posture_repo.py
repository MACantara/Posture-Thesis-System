import asyncpg

from app.db.interfaces import PostureRecord, PostureRepository, PostureStats
from app.db.postgresql.connection import get_connection, release_connection


class PostgresPostureRepository(PostureRepository):
    async def insert(self, user_id: int, status: str, angle: float,
                     duration: float | None = None, session_id: int | None = None,
                     notes: str | None = None) -> PostureRecord:
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """INSERT INTO posture_records (user_id, session_id, status, angle, duration, notes)
                   VALUES ($1, $2, $3, $4, $5, $6)
                   RETURNING *""",
                user_id, session_id, status, angle, duration, notes,
            )
            return PostureRecord(
                id=row["id"],
                user_id=row["user_id"],
                session_id=row["session_id"],
                timestamp=row["timestamp"].isoformat() if row["timestamp"] else None,
                status=row["status"],
                angle=row["angle"],
                duration=row["duration"],
                notes=row["notes"],
            )
        finally:
            await release_connection(conn)

    async def get_by_user(self, user_id: int, status_filter: str | None = None,
                          limit: int = 50, offset: int = 0) -> list[PostureRecord]:
        query = "SELECT * FROM posture_records WHERE user_id = $1"
        params: list = [user_id]
        param_idx = 2
        
        if status_filter and status_filter != "all":
            query += f" AND status = ${param_idx}"
            params.append(status_filter)
            param_idx += 1
        
        query += f" ORDER BY timestamp DESC LIMIT ${param_idx} OFFSET ${param_idx + 1}"
        params.extend([limit, offset])
        
        conn = await get_connection()
        try:
            rows = await conn.fetch(query, *params)
            return [
                PostureRecord(
                    id=row["id"],
                    user_id=row["user_id"],
                    session_id=row["session_id"],
                    timestamp=row["timestamp"].isoformat() if row["timestamp"] else None,
                    status=row["status"],
                    angle=row["angle"],
                    duration=row["duration"],
                    notes=row["notes"],
                )
                for row in rows
            ]
        finally:
            await release_connection(conn)

    async def get_stats(self, user_id: int) -> PostureStats:
        conn = await get_connection()
        try:
            # Total sessions
            row = await conn.fetchrow(
                "SELECT COUNT(*) as total FROM sessions WHERE user_id = $1", user_id
            )
            total_sessions = row["total"]

            # Good posture count
            row = await conn.fetchrow(
                "SELECT COUNT(*) as count FROM posture_records WHERE user_id = $1 AND status = 'good'",
                user_id,
            )
            good_count = row["count"]

            # Average angle
            row = await conn.fetchrow(
                "SELECT AVG(angle) as avg_angle FROM posture_records WHERE user_id = $1",
                user_id,
            )
            avg_angle = row["avg_angle"] if row["avg_angle"] is not None else 0.0

            # Current overall rate
            row = await conn.fetchrow(
                """SELECT
                    CAST(SUM(CASE WHEN status = 'good' THEN 1 ELSE 0 END) AS FLOAT)
                    / NULLIF(COUNT(*), 0) as rate
                   FROM posture_records WHERE user_id = $1""",
                user_id,
            )
            current_rate = row["rate"] if row["rate"] is not None else 0.0

            # Recent rate (last 7 days)
            row = await conn.fetchrow(
                """SELECT
                    CAST(SUM(CASE WHEN status = 'good' THEN 1 ELSE 0 END) AS FLOAT)
                    / NULLIF(COUNT(*), 0) as rate
                   FROM posture_records
                   WHERE user_id = $1 AND timestamp >= NOW() - INTERVAL '7 days'""",
                user_id,
            )
            recent_rate = row["rate"] if row["rate"] is not None else 0.0

            improvement_rate = recent_rate - current_rate

            return PostureStats(
                total_sessions=total_sessions,
                good_posture_count=good_count,
                average_angle=round(avg_angle, 2),
                improvement_rate=round(improvement_rate, 2),
            )
        finally:
            await release_connection(conn)
