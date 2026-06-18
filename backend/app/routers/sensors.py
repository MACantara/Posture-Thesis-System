from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/api/sensors", tags=["sensors"])

MOCK_SENSORS = [
    {
        "name": "MPU6050 — Upper Back",
        "online": True,
        "battery": 87,
        "signal": 92,
        "temperature": 36.5,
        "ping": 12,
    },
    {
        "name": "MPU6050 — Lower Back",
        "online": True,
        "battery": 73,
        "signal": 88,
        "temperature": 36.2,
        "ping": 15,
    },
    {
        "name": "Servo Motor",
        "online": True,
        "battery": 95,
        "signal": 100,
        "temperature": 35.8,
        "ping": 8,
    },
    {
        "name": "Vibrator Module",
        "online": False,
        "battery": 0,
        "signal": 0,
        "temperature": 0,
        "ping": 0,
    },
]


@router.get("/status")
async def get_sensor_status(current_user: dict = Depends(get_current_user)):
    return MOCK_SENSORS
