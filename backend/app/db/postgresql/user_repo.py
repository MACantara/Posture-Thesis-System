from datetime import datetime

import asyncpg

from app.db.interfaces import User, UserRepository
from app.db.postgresql.connection import get_connection, release_connection


class PostgresUserRepository(UserRepository):
    async def get_by_username(self, username: str) -> User | None:
        conn = await get_connection()
        try:
            row = await conn.fetchrow("SELECT * FROM users WHERE username = $1", username)
            if row is None:
                return None
            return User(
                id=row["id"],
                username=row["username"],
                password_hash=row["password_hash"],
                role=row["role"],
                location=row["location"],
                created_at=row["created_at"].isoformat() if row["created_at"] else None,
            )
        finally:
            await release_connection(conn)

    async def get_by_id(self, user_id: int) -> User | None:
        conn = await get_connection()
        try:
            row = await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id)
            if row is None:
                return None
            return User(
                id=row["id"],
                username=row["username"],
                password_hash=row["password_hash"],
                role=row["role"],
                location=row["location"],
                created_at=row["created_at"].isoformat() if row["created_at"] else None,
            )
        finally:
            await release_connection(conn)

    async def create(self, username: str, password_hash: str, role: str,
                     location: str | None = None) -> User:
        conn = await get_connection()
        try:
            row = await conn.fetchrow(
                """INSERT INTO users (username, password_hash, role, location)
                   VALUES ($1, $2, $3, $4)
                   RETURNING *""",
                username, password_hash, role, location,
            )
            return User(
                id=row["id"],
                username=row["username"],
                password_hash=row["password_hash"],
                role=row["role"],
                location=row["location"],
                created_at=row["created_at"].isoformat() if row["created_at"] else None,
            )
        finally:
            await release_connection(conn)

    async def list_all(self) -> list[User]:
        conn = await get_connection()
        try:
            rows = await conn.fetch("SELECT * FROM users ORDER BY id")
            return [
                User(
                    id=row["id"],
                    username=row["username"],
                    password_hash=row["password_hash"],
                    role=row["role"],
                    location=row["location"],
                    created_at=row["created_at"].isoformat() if row["created_at"] else None,
                )
                for row in rows
            ]
        finally:
            await release_connection(conn)

    async def update(self, user_id: int, **fields) -> User | None:
        allowed = {"username", "password_hash", "role", "location"}
        updates = {k: v for k, v in fields.items() if k in allowed}
        if not updates:
            return await self.get_by_id(user_id)
        
        set_clause = ", ".join(f"{k} = ${i+1}" for i, k in enumerate(updates.keys()))
        values = list(updates.values())
        
        conn = await get_connection()
        try:
            await conn.execute(
                f"UPDATE users SET {set_clause} WHERE id = ${len(values)+1}",
                *values, user_id
            )
            return await self.get_by_id(user_id)
        finally:
            await release_connection(conn)
