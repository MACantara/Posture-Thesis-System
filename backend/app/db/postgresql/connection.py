import asyncpg

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id            SERIAL PRIMARY KEY,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'user',
    location      TEXT,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    id            SERIAL PRIMARY KEY,
    user_id       INTEGER NOT NULL REFERENCES users(id),
    start_time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time      TIMESTAMP,
    good_count    INTEGER DEFAULT 0,
    warning_count INTEGER DEFAULT 0,
    poor_count    INTEGER DEFAULT 0,
    avg_angle     REAL
);

CREATE TABLE IF NOT EXISTS posture_records (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    session_id  INTEGER REFERENCES sessions(id),
    timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status      TEXT NOT NULL,
    angle       REAL NOT NULL,
    duration    REAL,
    notes       TEXT
);

CREATE INDEX IF NOT EXISTS idx_posture_user ON posture_records(user_id);
CREATE INDEX IF NOT EXISTS idx_posture_session ON posture_records(session_id);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);
"""

# Global connection pool
_pool: asyncpg.Pool | None = None


async def init_db(database_url: str) -> None:
    """Initialize database schema and create connection pool."""
    global _pool
    _pool = await asyncpg.create_pool(database_url, min_size=2, max_size=10)
    
    async with _pool.acquire() as conn:
        await conn.execute(SCHEMA_SQL)


async def get_connection() -> asyncpg.Connection:
    """Get a connection from the pool."""
    if _pool is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return await _pool.acquire()


async def release_connection(conn: asyncpg.Connection) -> None:
    """Release a connection back to the pool."""
    if _pool is not None:
        await _pool.release(conn)


async def close_pool() -> None:
    """Close the connection pool."""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None
