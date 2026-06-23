import logging
from datetime import datetime

import aiosqlite

from app.db.interfaces import User, UserRepository
from app.config import settings

logger = logging.getLogger(__name__)


class SqliteUserRepository(UserRepository):
    def __init__(self, db_path=None):
        self._db_path = str(db_path) if db_path else str(settings.db_path)
        logger.info("[SqliteUserRepo] initialized with db_path=%s", self._db_path)

    async def get_by_username(self, username: str) -> User | None:
        logger.info("[SqliteUserRepo] get_by_username: db_path=%s username=%s", self._db_path, username)
        try:
            async with aiosqlite.connect(self._db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("SELECT * FROM users WHERE username = ?", (username,))
                row = await cursor.fetchone()
                logger.info("[SqliteUserRepo] query result: username=%s row=%s", username, row is not None)
                if row is None:
                    return None
                return User(
                    id=row["id"],
                    username=row["username"],
                    password_hash=row["password_hash"],
                    role=row["role"],
                    location=row["location"],
                    created_at=row["created_at"],
                )
        except Exception as e:
            logger.error("[SqliteUserRepo] DB error: db_path=%s username=%s error=%s", self._db_path, username, e)
            raise

    async def get_by_id(self, user_id: int) -> User | None:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = await cursor.fetchone()
            if row is None:
                return None
            return User(
                id=row["id"],
                username=row["username"],
                password_hash=row["password_hash"],
                role=row["role"],
                location=row["location"],
                created_at=row["created_at"],
            )

    async def create(self, username: str, password_hash: str, role: str,
                     location: str | None = None) -> User:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "INSERT INTO users (username, password_hash, role, location) VALUES (?, ?, ?, ?)",
                (username, password_hash, role, location),
            )
            await db.commit()
            user_id = cursor.lastrowid
            return User(
                id=user_id,
                username=username,
                password_hash=password_hash,
                role=role,
                location=location,
                created_at=datetime.now().isoformat(),
            )

    async def list_all(self) -> list[User]:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT * FROM users ORDER BY id")
            rows = await cursor.fetchall()
            return [
                User(
                    id=row["id"],
                    username=row["username"],
                    password_hash=row["password_hash"],
                    role=row["role"],
                    location=row["location"],
                    created_at=row["created_at"],
                )
                for row in rows
            ]

    async def update(self, user_id: int, **fields) -> User | None:
        allowed = {"username", "password_hash", "role", "location"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return await self.get_by_id(user_id)
        set_clause = ", ".join(f"{k} = ?" for k in updates)
        values = list(updates.values()) + [user_id]
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(f"UPDATE users SET {set_clause} WHERE id = ?", values)
            await db.commit()
        return await self.get_by_id(user_id)
