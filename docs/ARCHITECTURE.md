# Architecture

## Overview

The Posture Thesis System uses a monorepo structure with a FastAPI backend and React frontend, designed for deployment on a Raspberry Pi 3 B+.

```
Posture-Thesis-System/
├── backend/           # FastAPI Python backend
│   ├── app/
│   │   ├── auth/      # JWT auth, password hashing, dependencies
│   │   ├── config.py  # Environment-based settings
│   │   ├── db/        # Repository pattern (SQLite + Supabase stubs)
│   │   ├── models/    # Pydantic schemas
│   │   ├── routers/   # API endpoints + WebSocket
│   │   ├── seed/      # Demo data seeding
│   │   ├── sensor/    # Mock + hardware sensor implementations
│   │   └── main.py    # FastAPI app entry point
│   ├── tests/         # pytest test suite
│   └── run.py         # Uvicorn launcher
├── frontend/          # React + TypeScript + Vite + TailwindCSS
│   └── src/
│       ├── api/       # Axios API clients
│       ├── components/# Dashboard widgets
│       ├── context/   # Auth context
│       ├── hooks/     # WebSocket hook
│       └── pages/     # Login + Dashboard pages
└── deploy/            # systemd service, deploy script
```

## Backend Architecture

### Database Layer (Repository Pattern)

- **Interfaces** (`db/interfaces.py`): Abstract base classes for `UserRepository`, `PostureRepository`, `SessionRepository`
- **SQLite Implementation** (`db/sqlite/`): Concrete repos using `aiosqlite`
- **Supabase Stubs** (`db/supabase/`): Placeholder for future cloud migration
- **Factory** (`db/factory.py`): Returns repos based on `DB_BACKEND` env var

### Authentication

- JWT-based with `python-jose`
- Password hashing with `bcrypt` (direct, not passlib)
- Role-based access: `user` and `admin`
- FastAPI dependencies: `get_current_user`, `require_admin`

### Sensor System

- **Mock sensors** (`sensor/mock_sensor.py`, `mock_motor.py`): Simulated MPU6050 + servo for development
- **Hardware sensors** (`sensor/mpu6050.py`, `servo.py`): Real I2C/GPIO implementations
- **Factory** (`sensor/factory.py`): Returns mock or hardware based on `USE_MOCK_SENSORS`
- **Posture detection** (`sensor/posture_detector.py`): Classifies angle into good/warning/poor
- **WebSocket** (`routers/websocket.py`): Real-time sensor data streaming with JWT auth

### API Routers

| Router | Prefix | Auth | Description |
|--------|--------|------|-------------|
| auth | `/api/auth` | Public + JWT | Login, get current user |
| posture | `/api/posture` | JWT | Records CRUD, stats |
| sessions | `/api/sessions` | JWT | Start/end monitoring sessions |
| users | `/api/users` | Admin | User management |
| sensors | `/api/sensors` | JWT | Sensor status |
| websocket | `/ws` | JWT (query) | Real-time sensor stream |

## Frontend Architecture

- **React 18+** with TypeScript
- **Vite** for build tooling
- **TailwindCSS** for styling (dark theme with cyan accents)
- **React Router** for navigation
- **Axios** for API calls with JWT interceptor
- **Recharts** for data visualization
- **Lucide React** for icons

### Pages

- `/login` — User login
- `/admin/login` — Admin login
- `/dashboard` — User dashboard (Home, Connectivity, Posture Status tabs)
- `/admin` — Admin dashboard (stats, user table, location map)

## Deployment

- **systemd** service for backend (uvicorn on port 80)
- uvicorn serves API, WebSocket, and built frontend static files
- SQLite database stored locally on Pi
- Frontend built and served as static files via FastAPI StaticFiles
