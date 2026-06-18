# Database Schema

## SQLite Schema

### users
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| username | TEXT | UNIQUE NOT NULL |
| password_hash | TEXT | NOT NULL |
| role | TEXT | NOT NULL DEFAULT 'user' |
| location | TEXT | |
| created_at | TEXT | DEFAULT CURRENT_TIMESTAMP |

### posture_records
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| user_id | INTEGER | NOT NULL REFERENCES users(id) |
| session_id | INTEGER | REFERENCES sessions(id) |
| timestamp | TEXT | DEFAULT CURRENT_TIMESTAMP |
| status | TEXT | NOT NULL |
| angle | REAL | NOT NULL |
| duration | REAL | |
| notes | TEXT | |

### sessions
| Column | Type | Constraints |
|--------|------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT |
| user_id | INTEGER | NOT NULL REFERENCES users(id) |
| start_time | TEXT | DEFAULT CURRENT_TIMESTAMP |
| end_time | TEXT | |
| good_count | INTEGER | DEFAULT 0 |
| warning_count | INTEGER | DEFAULT 0 |
| poor_count | INTEGER | DEFAULT 0 |
| avg_angle | REAL | |

## Entity Relationships

```
users (1) ──< (N) sessions
users (1) ──< (N) posture_records
sessions (1) ──< (N) posture_records
```

## Migration Path to Supabase

The repository pattern abstracts database access:

1. **Current**: `SqliteUserRepository`, `SqlitePostureRepository`, `SqliteSessionRepository`
2. **Future**: `SupabaseUserRepository`, `SupabasePostureRepository`, `SupabaseSessionRepository`

To migrate:
1. Implement the stubs in `db/supabase/`
2. Set `DB_BACKEND=supabase` in `.env`
3. The factory (`db/factory.py`) will automatically use the new repos

No router or frontend changes needed — the repository interface remains the same.
