import asyncio
import re
import time

from fastapi import APIRouter, Depends

from app.auth.dependencies import get_current_user
from app.sensor.factory import get_sensor, get_motor
from app.sensor.detector import (
    detect_all_hardware,
    read_detected_sensor_status,
    read_detected_motor_status,
    _scan_network_devices,
    _get_local_network_info,
)

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


@router.get("/status")
async def get_sensor_status(current_user: dict = Depends(get_current_user)):
    """Return status of all detected sensors and motors on the Pi."""
    sensor_statuses = await read_detected_sensor_status()
    motor_statuses = await read_detected_motor_status()

    results = []
    for s in sensor_statuses:
        results.append({
            "name": s["name"],
            "online": s["online"],
            "battery": s["battery"],
            "signal": s["signal"],
            "temperature": s["temperature"],
            "ping": s["ping"],
        })
    for m in motor_statuses:
        results.append({
            "name": m["name"],
            "online": m["online"],
            "battery": m["battery"],
            "signal": m["signal"],
            "temperature": m["temperature"],
            "ping": m["ping"],
        })

    if not results:
        results.append({
            "name": "No sensors detected",
            "online": False,
            "battery": 0,
            "signal": 0,
            "temperature": 0,
            "ping": 0,
        })

    return results


@router.get("/detect")
async def detect_hardware(current_user: dict = Depends(get_current_user)):
    """Detect all connected hardware on the Raspberry Pi (I2C, GPIO, BLE)."""
    return await detect_all_hardware()


@router.get("/bluetooth")
async def get_bluetooth_status(current_user: dict = Depends(get_current_user)):
    return await _read_bluetooth_adapter()


@router.get("/network")
async def get_network_devices(current_user: dict = Depends(get_current_user)):
    """Discover devices on the local network."""
    devices = await _scan_network_devices()
    local_info = _get_local_network_info()
    return {
        "local": local_info,
        "devices": devices,
    }
