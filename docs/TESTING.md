# Testing

## Backend Tests

### Setup
```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt
```

### Run Tests
```bash
# All tests
python -m pytest -v

# Specific test file
python -m pytest tests/test_auth.py -v

# With coverage
python -m pytest --cov=app --cov-report=term-missing
```

### Test Structure

| File | Tests | Description |
|------|-------|-------------|
| test_health.py | 1 | Health check endpoint |
| test_auth.py | 7 | Login, token validation, /me endpoint |
| test_posture.py | 6 | Records CRUD, filtering, stats |
| test_sessions.py | 3 | Session start/end, listing |
| test_users.py | 6 | Admin user management, RBAC |
| test_sensors.py | 2 | Sensor status endpoint |
| test_seed.py | 2 | Seed data creation |
| test_sensor.py | 9 | Mock sensor, motor, posture detector |
| test_websocket.py | 5 | WebSocket auth, data streaming, commands |

### Test Fixtures (conftest.py)

- `temp_db_path` — Temporary SQLite database
- `app_instance` — FastAPI app with seeded users
- `client` — Async HTTPX test client
- `user_token` / `admin_token` — JWT tokens for auth
- `auth_headers` / `admin_headers` — Authorization headers

### Writing New Tests

```python
import pytest

@pytest.mark.asyncio
async def test_my_endpoint(client, auth_headers):
    response = await client.get("/api/my-endpoint", headers=auth_headers)
    assert response.status_code == 200
```

## Frontend

TypeScript type checking:
```bash
cd frontend
npx tsc --noEmit
```

Build verification:
```bash
npm run build
```
