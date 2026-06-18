# Posture Thesis System

An Intelligent Wearable Sensor-Based System for Posture Detection and Real-Time Feedback Correction.

## Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
cp ../.env.example ../.env
python -m app.seed.seed_data  # Seed demo users and posture records
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`.

### Default Credentials

| Role | Username | Password |
|---|---|---|
| User | `user` | `pass123` |
| Admin | `admin` | `admin123` |

### Running Tests

```bash
cd backend
pytest --cov=app --cov-report=term-missing
```

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.9+, FastAPI, uvicorn |
| Database | SQLite (aiosqlite), repository pattern abstraction |
| Auth | passlib[bcrypt], python-jose JWT |
| Frontend | React 18, TypeScript, Vite, TailwindCSS |
| Charts | Recharts |
| Real-time | FastAPI WebSockets |
| Sensors | MPU6050 via I2C (mock mode for development) |
| Testing | pytest, pytest-asyncio, httpx, pytest-cov |

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — system design and component overview
- [Hardware Integration](docs/HARDWARE-INTEGRATION.md) — wiring and sensor setup
- [Deployment](docs/DEPLOYMENT.md) — Raspberry Pi deployment guide
- [API Reference](docs/API-REFERENCE.md) — REST and WebSocket endpoints
- [Database Schema](docs/DATABASE-SCHEMA.md) — table definitions and migration guide
- [Testing](docs/TESTING.md) — test structure and coverage

## License

MIT — see [LICENSE](LICENSE).
