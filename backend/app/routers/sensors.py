import time

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.sensor.factory import get_sensor, get_motor

router = APIRouter(prefix="/api/sensors", tags=["sensors"])

sensor = None
motor = None


def get_sensor_instance():
    global sensor
    if sensor is None:
        sensor = get_sensor()
    return sensor


def get_motor_instance():
    global motor
    if motor is None:
        motor = get_motor()
    return motor


async def _read_sensor_status() -> dict:
    """Read actual status from the sensor instance."""
    sens = get_sensor_instance()
    try:
        t0 = time.monotonic()
        temp = await sens.read_temperature()
        ping_ms = round((time.monotonic() - t0) * 1000, 1)
        return {
            "name": "MPU6050 Sensor",
            "online": True,
            "battery": 0,
            "signal": 0,
            "temperature": temp,
            "ping": ping_ms,
        }
    except Exception:
        return {
            "name": "MPU6050 Sensor",
            "online": False,
            "battery": 0,
            "signal": 0,
            "temperature": 0,
            "ping": 0,
        }


async def _read_motor_status(name: str) -> dict:
    """Read actual status from the motor instance."""
    mot = get_motor_instance()
    try:
        return {
            "name": name,
            "online": True,
            "battery": 0,
            "signal": 0,
            "temperature": 0,
            "ping": 0,
        }
    except Exception:
        return {
            "name": name,
            "online": False,
            "battery": 0,
            "signal": 0,
            "temperature": 0,
            "ping": 0,
        }


@router.get("/status")
async def get_sensor_status(current_user: dict = Depends(get_current_user)):
    return [
        await _read_sensor_status(),
        await _read_motor_status("Servo Motor"),
        await _read_motor_status("Vibrator Module"),
    ]
