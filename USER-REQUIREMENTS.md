# Posture Thesis System User Requirements

## Project Title

An Intelligent Wearable Sensor-Based System for Posture Detection and Real-Time Feedback Correction

## Hardware Components List

- Vest
- Raspberry Pi 3 B+
- Servo motor (For posture correction)
- Vibrator motor (for alert feedback apparently)
- MPU6050 sensor 
- 9V battery

## Expected Features

- Posture detection
- Real-time feedback correction
  - Servo motor provides physical posture correction adjustment
  - Vibrator motor provides haptic alert feedback when poor posture is detected
- Login page (Email & Password) for users and admin
  - Modern, professional design with a kinetic dark card, cyan gradient button, and grid-line background overlay
  - Password visibility toggle
  - Link to switch between user and admin login
- Dashboard with 3 tabs (Home, Connectivity, Posture Status)
- Home tab summary statistics (Total sessions, Good posture count, Average angle, Improvement rate)
- Posture records table with filtering tabs (All Records, Good Posture, Warnings)
  - Each record shows timestamp, status (good/warning/poor), duration, angle, and notes
  - Color-coded badges and icons for quick status identification
- Web app
- Animated upper-body figure to visualize posture (green = good, red = poor, amber = warning)
- Connectivity using Bluetooth (BLE 5.0)
  - Sensor cards showing battery, signal, temperature, ping, and online/offline status
  - Wireless metadata panel
- Admin dashboard with user list, locations, and status overview
- Data persistence via SQLite (primary): local database on the Pi, no internet dependency
- Database abstraction layer allowing future migration to Supabase (cloud) with minimal code changes
- Planned trained AI model with dataset (still unclear on this aspect)

## UI

### User Login

- Credentials: username `user` / password `pass123`
- Kinetic dark card with cyan gradient button
- Password visibility toggle
- Grid-line background overlay
- Link to switch to admin login
- Secure session handling via JWT (works with both SQLite and future Supabase migration)

### Home tab

- Stat cards:
  - Total sessions
  - Good posture rate
  - Average angle
  - Improvement rate
- Donut chart showing percentage of good and poor posture
- Personalized activity recommendations for time periods with poor posture
- Filterable posture records table with color-coded status badges and angle columns

### Connectivity Tab

- Sensor connection cards showing:
  - Functional status (online/offline)
  - Battery level bar
  - Signal strength
  - Temperature
  - Ping/latency
- Bluetooth metadata panel (BLE connection details, signal strength, battery)

### Posture Status Tab

- Animated glowing upper-body SVG silhouette
  - Green = good posture
  - Red = poor posture
  - Amber = warning
- Demo toggle buttons to switch between posture states
- Live joint angle bars with smooth transitions
- Session stats
- Recalibrate button

### Admin Login

- Credentials: username `admin` / password `admin123`
- Same login shell as user login with shield icon and "Administrator Portal" label
- Password visibility toggle

### Admin Dashboard

- Stat row summarizing system-wide posture metrics
- Searchable user table with:
  - Initials avatars
  - Location and region
  - Good-rate progress bars
  - Recent activity status
- Stylized location map with region markers showing user distribution
  - City/region labels
  - Dot-based visualization
- User management controls (view, edit, deactivate)

## Tech Stack

### Backend — Python + FastAPI

- Python for natural I2C sensor communication (`smbus2`, `RPi.GPIO`)
- FastAPI: lightweight, async, built-in WebSocket support for real-time posture data streaming
- Runs directly on the Pi, reads sensors, and serves built frontend as static files
- `uvicorn` with 1-2 workers (more workers will consume too much RAM on the Pi 3 B+)

### Frontend — React + Vite + TailwindCSS

- Build on a dev machine, deploy built static files (`dist/`) to the Pi — Pi only serves static HTML/JS/CSS
- Recharts for donut chart and posture percentage charts
- Lucide for icons
- Matches the modern UI design specified in the UI section above

### Database & Auth — SQLite (Primary) with Abstraction Layer

#### Primary Database: SQLite (Local on Pi)

- `aiosqlite` for async SQLite access from FastAPI
- Local `posture.db` file stored on the Pi's SD card
- Zero internet dependency — works fully offline
- ~0ms query latency (local file I/O)
- Minimal RAM usage
- `users` table with `role` column (`user` or `admin`) for role-based access control
- Auth using:
  - `passlib[bcrypt]` for password hashing
  - `python-jose` for JWT generation and verification
  - FastAPI `OAuth2PasswordBearer` for protecting routes

#### Auth Flow

```
Login page → POST /api/auth/login → FastAPI checks users table (via DB abstraction layer)
  → role = "user"  → return JWT → frontend routes to User Dashboard
  → role = "admin" → return JWT → frontend routes to Admin Dashboard

All subsequent requests include JWT in Authorization header
FastAPI verifies JWT + checks role before responding
```

#### Database Abstraction Layer

The system uses a **repository pattern** so the application logic never touches DB-specific code directly. This allows swapping SQLite for Supabase/PostgreSQL in the future with minimal changes.

```
db/
  ├── interfaces.py       # Abstract repository interfaces (UserRepository, PostureRepository, SessionRepository)
  ├── sqlite/
  │   ├── connection.py   # SQLite connection management (aiosqlite)
  │   ├── user_repo.py    # SQLite implementation of UserRepository
  │   ├── posture_repo.py # SQLite implementation of PostureRepository
  │   └── session_repo.py # SQLite implementation of SessionRepository
  ├── supabase/           # Future: Supabase implementations (stub for now)
  │   ├── client.py       # Supabase client setup
  │   ├── user_repo.py    # Supabase implementation of UserRepository
  │   ├── posture_repo.py # Supabase implementation of PostureRepository
  │   └── session_repo.py # Supabase implementation of SessionRepository
  └── factory.py          # Returns the correct repository implementations based on config
```

- `factory.py` reads a config flag (e.g. `DB_BACKEND = "sqlite"` or `"supabase"`) to select implementations
- All API routes and business logic depend only on the abstract interfaces — never on concrete DB implementations
- When migrating to Supabase, only the `db/supabase/` implementations need to be filled in — the rest of the app stays unchanged

```python
# interfaces.py — abstract repository interfaces
class UserRepository:
    async def get_by_username(self, username: str) -> User | None: ...
    async def create(self, username: str, password_hash: str, role: str) -> User: ...
    async def list_all(self) -> list[User]: ...

class PostureRepository:
    async def insert(self, record: PostureRecord) -> PostureRecord: ...
    async def get_by_user(self, user_id: int, filters: dict) -> list[PostureRecord]: ...
    async def get_stats(self, user_id: int) -> PostureStats: ...

class SessionRepository:
    async def start_session(self, user_id: int) -> int: ...
    async def end_session(self, session_id: int) -> None: ...
    async def get_by_user(self, user_id: int) -> list[Session]: ...
```

#### Database Schema (Shared Across All Backends)

```sql
-- users table
CREATE TABLE users (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    username    TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role        TEXT NOT NULL DEFAULT 'user',  -- 'user' or 'admin'
    location    TEXT,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- posture_records table
CREATE TABLE posture_records (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    session_id  INTEGER REFERENCES sessions(id),
    timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status      TEXT NOT NULL,               -- 'good', 'warning', 'poor'
    angle       REAL NOT NULL,               -- posture angle in degrees
    duration    REAL,                        -- duration in seconds
    notes       TEXT
);

-- sessions table
CREATE TABLE sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    start_time  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time    TIMESTAMP,
    good_count  INTEGER DEFAULT 0,
    warning_count INTEGER DEFAULT 0,
    poor_count  INTEGER DEFAULT 0,
    avg_angle   REAL
);
```

- Schema is written in standard SQL compatible with both SQLite and PostgreSQL
- For Supabase migration: `AUTOINCREMENT` → `GENERATED ALWAYS AS IDENTITY`, `TIMESTAMP` → `TIMESTAMPTZ`
- Row-level security policies added in Supabase for per-user data isolation

#### Future Migration Path: Supabase (Cloud)

- PostgreSQL for posture records, user accounts, and sessions
- Built-in auth with user and admin roles via row-level security
- Real-time subscriptions for live data sync
- Offloads database load from the Pi (critical given 1GB RAM constraint)
- Migration steps:
  1. Create Supabase project and tables (same schema, PostgreSQL syntax)
  2. Implement `db/supabase/` repository classes using `supabase-py`
  3. Set `DB_BACKEND = "supabase"` in config
  4. Export SQLite data → import to Supabase PostgreSQL
  5. Replace DIY auth with Supabase Auth (JWT structure stays the same)
  6. Frontend changes are minimal — same API endpoints, same JWT format
- **Supabase client strategy (when migrated)**:
  - Frontend auth: Supabase JS client (direct from browser)
  - Backend auth verification: `supabase-py` (`auth.get_user(jwt)`)
  - Posture record CRUD: `supabase-py` (`table().insert/select`)
  - **Trade-off**: `supabase-py` uses HTTP REST (PostgREST) for each DB operation, adding ~50-200ms latency per query — acceptable for moderate data volume
  - **Fallback**: If query latency is an issue, swap to `asyncpg` for direct PostgreSQL connections and keep `supabase-py` only for auth verification

### Real-time Communication — WebSockets (via FastAPI)

- Streams live sensor data and posture status from Pi to connected client devices
- Low overhead, bidirectional communication

### Sensor Integration — Python

- `smbus2` for I2C communication with MPU6050
- `numpy` for angle/posture calculations
- Posture detection logic runs on the Pi itself

### Sensor Data Reading & Hardware Integration

#### Current Status

- Hardware (sensors, motors, vest) is **not yet available**
- Web app and backend are being developed with the sensor abstraction layer ready for hardware integration
- Sensor abstraction layer is designed so real hardware can be plugged in with minimal code changes

#### Sensor Abstraction Layer Design

The system uses an **interface-based approach** so hardware implementations are interchangeable:

```
sensor/
  ├── interfaces.py      # Abstract base classes (SensorInterface, MotorInterface)
  ├── mpu6050.py         # MPU6050 implementation (uses smbus2)
  ├── servo.py           # Servo motor control (uses RPi.GPIO)
  └── factory.py         # Factory that returns hardware implementations
```

- `factory.py` returns hardware sensor and motor instances
- When hardware is connected, `mpu6050.py` and `servo.py` read real data — the rest of the app stays unchanged

#### MPU6050 Sensor — Raw Data Reading

- **Communication**: I2C via `smbus2` (address `0x68` by default)
- **Registers to read**:
  - Accelerometer X, Y, Z (registers `0x3B–0x40`)
  - Gyroscope X, Y, Z (registers `0x43–0x48`)
  - Temperature (registers `0x41–0x42`)
- **Data processing**:
  - Raw 16-bit values converted to physical units (accel: `g`, gyro: `°/s`)
  - Complementary filter or Kalman filter to fuse accel + gyro for stable angle estimation
  - `numpy` used for vectorized calculations
- **Sampling rate**: configurable (default 10Hz for logging, higher for real-time feedback)
- **Calibration**: offset values stored in config, applied on read

```python
# interfaces.py — abstract base class
class SensorInterface:
    async def read_accel(self) -> tuple[float, float, float]: ...  # (x, y, z) in g
    async def read_gyro(self) -> tuple[float, float, float]: ...   # (x, y, z) in deg/s
    async def read_temperature(self) -> float: ...                  # in Celsius
    async def get_posture_angle(self) -> float: ...                 # fused angle in degrees

class MotorInterface:
    async def correct_posture(self, angle: float) -> None: ...     # servo adjustment
    async def alert_feedback(self, intensity: float) -> None: ...  # vibrator pulse
```

#### Servo Motor — Posture Correction Control

- **Control**: PWM via `RPi.GPIO` (GPIO pin configurable in config)
- **Behavior**: adjusts servo angle based on detected posture deviation

#### Vibrator Motor — Alert Feedback Control

- **Control**: GPIO digital output (on/off) or PWM for intensity
- **Behavior**: triggers haptic pulse when poor posture detected for sustained period

#### Sensor Data Reading

- Reads actual accelerometer and gyroscope values from the MPU6050:
  - Good posture (small deviations from neutral)
  - Poor posture (larger deviations, slouching patterns)
  - Transitions between postures over time
- Data follows the `SensorInterface` — app code is identical across deployments
- Real-time data streamed via WebSocket for live posture monitoring

#### Integration Checklist (When Hardware Arrives)

1. Connect MPU6050 to Pi I2C pins (SDA/SCL, VCC, GND)
2. Enable I2C on the Pi (`raspi-config` → Interfacing Options → I2C)
3. Verify I2C detection: `i2cdetect -y 1` (should show `0x68`)
4. Connect servo motor to designated GPIO pin
5. Connect vibrator motor to designated GPIO pin
6. Install hardware drivers: `pip install smbus2 RPi.GPIO`
7. Calibrate MPU6050 offsets (run calibration script, save to config)
8. Test real-time sensor reading via WebSocket
9. Tune posture detection thresholds with real data
10. Test servo correction and vibrator feedback with real motors

### Deployment Architecture

```
[Raspberry Pi 3 B+]
  ├── MPU6050 sensors (I2C)
  ├── FastAPI backend (Python)
  │     ├── Sensor reading + posture detection
  │     ├── Servo motor control (posture correction)
  │     ├── Vibrator motor control (alert feedback)
  │     ├── WebSocket server (real-time data)
  │     └── Serves built React static files
  └── SQLite database (local posture.db file on SD card)

[Client devices (phone/laptop)]
  └── Browser → accesses Pi's web app via local network IP
```

#### Production Architecture (with Supabase)

```
[Raspberry Pi 3 B+]
  ├── MPU6050 sensors (I2C)
  ├── FastAPI backend (Python)
  │     ├── Sensor reading + posture detection
  │     ├── Servo motor control (posture correction)
  │     ├── Vibrator motor control (alert feedback)
  │     ├── WebSocket server (real-time data)
  │     └── Serves built React static files
  └── Connects to Supabase (cloud) for auth + DB

[Client devices (phone/laptop)]
  └── Browser → accesses Pi's web app via local network IP
```

### Pi 3 B+ Constraints & Considerations

- Do not run a dev server on the Pi — always build the React app elsewhere and copy `dist/` to the Pi
- Use `uvicorn` with 1-2 workers max (more workers will eat RAM)
- SQLite (local file) is the primary database — no external service dependency, works offline
- Database abstraction layer allows future migration to Supabase (cloud) with minimal code changes
- Supabase migration offloads DB to cloud, saving ~200-400MB RAM on the Pi (future, not required for current scope)

## Documentation Files

The project includes the following documentation to explain the system clearly:

- **`README.md`** (root) — project overview, quick start, dev commands, tech stack summary, links to all other docs
- **`docs/ARCHITECTURE.md`** — system architecture overview, component diagram, request flow, sensor abstraction layer, database abstraction layer, folder structure explanation
- **`docs/HARDWARE-INTEGRATION.md`** — wiring diagrams (MPU6050 → Pi I2C, servo → GPIO, vibrator → GPIO), step-by-step switchover from mock to real sensors, calibration instructions, troubleshooting guide
- **`docs/DEPLOYMENT.md`** — step-by-step Pi deployment: environment setup, building frontend, copying files, systemd service config, network access, production architecture diagram (with Supabase upgrade path)
- **`docs/API-REFERENCE.md`** — all REST endpoints documented: auth, posture, sessions, users, sensors, WebSocket — with request/response examples and auth requirements
- **`docs/DATABASE-SCHEMA.md`** — table definitions, relationships, ERD diagram, repository pattern explanation, SQLite → Supabase migration guide
- **`docs/TESTING.md`** — how to run tests, test structure, coverage commands, what each test file covers, how to add new tests
