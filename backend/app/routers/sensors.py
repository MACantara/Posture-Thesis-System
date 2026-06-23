import asyncio
import re
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


async def _read_bluetooth_adapter() -> dict:
    """Check the Raspberry Pi's built-in Bluetooth 4.2/BLE adapter (hci0)."""
    def _check_hci0() -> dict:
        import subprocess

        try:
            result = subprocess.run(
                ["hciconfig", "hci0"],
                capture_output=True, text=True, timeout=5,
            )
            output = result.stdout

            if not output:
                return {
                    "name": "Built-in Bluetooth 4.2/BLE",
                    "online": False,
                    "address": None,
                    "up": False,
                    "connected_devices": 0,
                }

            online = "UP" in output
            address_match = re.search(r"BD Address:\s*([0-9A-Fa-f:]{17})", output)
            address = address_match.group(1) if address_match else None

            connected = 0
            try:
                bt_result = subprocess.run(
                    ["btconn", "-l"],
                    capture_output=True, text=True, timeout=5,
                )
                if bt_result.returncode == 0 and bt_result.stdout.strip():
                    connected = len([l for l in bt_result.stdout.strip().split("\n") if l.strip()])
            except Exception:
                pass

            return {
                "name": "Built-in Bluetooth 4.2/BLE",
                "online": online,
                "address": address,
                "up": online,
                "connected_devices": connected,
            }
        except FileNotFoundError:
            return {
                "name": "Built-in Bluetooth 4.2/BLE",
                "online": False,
                "address": None,
                "up": False,
                "connected_devices": 0,
            }
        except Exception:
            return {
                "name": "Built-in Bluetooth 4.2/BLE",
                "online": False,
                "address": None,
                "up": False,
                "connected_devices": 0,
            }

    return await asyncio.to_thread(_check_hci0)


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


@router.get("/bluetooth")
async def get_bluetooth_status(current_user: dict = Depends(get_current_user)):
    return await _read_bluetooth_adapter()
