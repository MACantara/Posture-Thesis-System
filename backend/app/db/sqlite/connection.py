from pathlib import Path

import aiosqlite

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role          TEXT NOT NULL DEFAULT 'user',
    location      TEXT,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sessions (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id       INTEGER NOT NULL REFERENCES users(id),
    start_time    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time      TIMESTAMP,
    good_count    INTEGER DEFAULT 0,
    warning_count INTEGER DEFAULT 0,
    poor_count    INTEGER DEFAULT 0,
    avg_angle     REAL
);

CREATE TABLE IF NOT EXISTS posture_records (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
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


async def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(db_path) as db:
        await db.executescript(SCHEMA_SQL)
        await db.commit()


async def get_connection(db_path: Path) -> aiosqlite.Connection:
    db = await aiosqlite.connect(str(db_path))
    db.row_factory = aiosqlite.Row
    return db
