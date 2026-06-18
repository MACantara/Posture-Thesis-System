# API Reference

## Authentication

### POST /api/auth/login
Login and receive JWT token.

**Request:**
```json
{
  "username": "user",
  "password": "pass123"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "role": "user",
  "username": "user"
}
```

**Errors:** 401 — Invalid credentials

---

### GET /api/auth/me
Get current authenticated user.

**Headers:** `Authorization: Bearer <token>`

**Response (200):**
```json
{
  "id": 1,
  "username": "user",
  "role": "user",
  "location": "Manila",
  "created_at": "2024-01-01T00:00:00"
}
```

---

## Posture Records

### GET /api/posture/records
Get posture records for the current user.

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| status | string | "all" | Filter: all, good, warning, poor |
| limit | int | 50 | Max records (1-200) |
| offset | int | 0 | Pagination offset |

**Response (200):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "session_id": 1,
    "timestamp": "2024-01-01T12:00:00",
    "status": "good",
    "angle": 5.2,
    "duration": 10.0,
    "notes": null
  }
]
```

---

### GET /api/posture/stats
Get aggregated posture statistics.

**Response (200):**
```json
{
  "total_sessions": 21,
  "good_posture_count": 120,
  "average_angle": 8.5,
  "improvement_rate": 15.0
}
```

---

### POST /api/posture/records
Create a posture record.

**Request:**
```json
{
  "status": "good",
  "angle": 5.2,
  "duration": 10.0,
  "session_id": 1
}
```

**Response (201):** Same as record object above.

---

## Sessions

### GET /api/sessions
List all sessions for the current user.

### POST /api/sessions/start
Start a new monitoring session.

**Response (200):**
```json
{
  "session_id": 42
}
```

### POST /api/sessions/{session_id}/end
End a monitoring session.

---

## Users (Admin Only)

### GET /api/users
List all users. **Requires admin role.**

### GET /api/users/{user_id}
Get a specific user. **Requires admin role.**

### PATCH /api/users/{user_id}
Update user fields. **Requires admin role.**

---

## Sensors

### GET /api/sensors/status
Get status of all connected sensors.

**Response (200):**
```json
[
  {
    "name": "MPU6050 — Upper Back",
    "online": true,
    "battery": 87,
    "signal": 92,
    "temperature": 36.5,
    "ping": 12
  }
]
```

---

## WebSocket

### WS /ws
Real-time sensor data stream.

**Connection:** `ws://<host>:8000/ws?token=<jwt>`

**Incoming messages (server → client):**
```json
{
  "angle": 5.2,
  "status": "good",
  "accel": { "x": 0.01, "y": 0.02, "z": 1.0 },
  "gyro": { "x": 0.1, "y": 0.0, "z": 0.0 },
  "temperature": 36.5,
  "timestamp": "2024-01-01T12:00:00.000"
}
```

**Outgoing commands (client → server):**
```json
{ "type": "recalibrate" }
{ "type": "set_demo_state", "state": "good" }
```

---

## Health Check

### GET /api/health
```json
{ "status": "ok" }
```
