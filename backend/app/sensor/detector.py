"""Hardware detection for Raspberry Pi 3 B+.

Scans I2C bus for connected sensors, checks GPIO availability for motors,
and scans BLE for connected Bluetooth devices.
"""

import asyncio
import logging
import subprocess

from app.config import settings

logger = logging.getLogger(__name__)

# Known I2C sensor addresses on the Pi 3 B+
KNOWN_I2C_DEVICES = {
    0x68: "MPU6050",
    0x69: "MPU6050 (alt addr)",
    0x76: "BME280",
    0x77: "BME280 (alt addr)",
    0x48: "ADS1115",
    0x1E: "HMC5883L",
}


def _scan_i2c_bus(bus_num: int) -> list[dict]:
    """Scan I2C bus for connected devices using smbus2."""
    try:
        import smbus2
    except ImportError:
        logger.warning("smbus2 not available — cannot scan I2C bus")
        return []

    devices = []
    try:
        bus = smbus2.SMBus(bus_num)
        for addr in range(0x03, 0x78):
            try:
                bus.read_byte(addr)
                name = KNOWN_I2C_DEVICES.get(addr, f"I2C device at 0x{addr:02X}")
                devices.append({
                    "name": name,
                    "address": f"0x{addr:02X}",
                    "bus": bus_num,
                    "interface": "I2C",
                })
                logger.info("I2C device detected: %s at 0x%02X on bus %d", name, addr, bus_num)
            except (OSError, IOError):
                pass
        bus.close()
    except Exception as e:
        logger.error("I2C bus scan failed: %s", e)
    return devices


def _check_gpio_pins() -> list[dict]:
    """Check if configured GPIO pins are available for motors."""
    try:
        import RPi.GPIO as GPIO
    except ImportError:
        logger.warning("RPi.GPIO not available — cannot check GPIO pins")
        return []

    devices = []
    pins = [
        {"pin": settings.SERVO_GPIO_PIN, "name": "Servo Motor", "type": "motor"},
        {"pin": settings.VIBRATOR_GPIO_PIN, "name": "Vibrator Module", "type": "motor"},
    ]
    try:
        GPIO.setmode(GPIO.BCM)
        for p in pins:
            try:
                GPIO.setup(p["pin"], GPIO.OUT)
                devices.append({
                    "name": p["name"],
                    "pin": p["pin"],
                    "interface": "GPIO",
                    "type": p["type"],
                })
                logger.info("GPIO device available: %s on pin %d", p["name"], p["pin"])
            except Exception as e:
                logger.warning("GPIO pin %d not available: %s", p["pin"], e)
    except Exception as e:
        logger.error("GPIO check failed: %s", e)
    return devices


def _scan_ble_devices() -> list[dict]:
    """Scan for BLE-connected devices using bluetoothctl."""
    devices = []
    try:
        result = subprocess.run(
            ["hcitool", "con"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split("\n")
            for line in lines:
                if "handle" in line.lower():
                    parts = line.strip().split()
                    addr = None
                    for part in parts:
                        if ":" in part and len(part) == 17:
                            addr = part
                            break
                    devices.append({
                        "name": f"BLE Device {addr}" if addr else "BLE Device",
                        "address": addr,
                        "interface": "BLE",
                    })
    except FileNotFoundError:
        logger.warning("hcitool not available — cannot scan BLE connections")
    except Exception as e:
        logger.warning("BLE scan failed: %s", e)
    return devices


async def detect_all_hardware() -> dict:
    """Detect all connected hardware on the Raspberry Pi.

    Returns a dict with 'i2c', 'gpio', and 'ble' lists.
    """
    i2c = await asyncio.to_thread(_scan_i2c_bus, settings.I2C_BUS)
    gpio = await asyncio.to_thread(_check_gpio_pins)
    ble = await asyncio.to_thread(_scan_ble_devices)

    return {
        "i2c": i2c,
        "gpio": gpio,
        "ble": ble,
    }


async def detect_sensors() -> list[dict]:
    """Detect all connected sensors (I2C + BLE)."""
    hardware = await detect_all_hardware()
    sensors = []
    for dev in hardware["i2c"]:
        sensors.append({
            "name": dev["name"],
            "online": True,
            "interface": dev["interface"],
            "address": dev.get("address"),
            "bus": dev.get("bus"),
        })
    for dev in hardware["ble"]:
        sensors.append({
            "name": dev["name"],
            "online": True,
            "interface": dev["interface"],
            "address": dev.get("address"),
        })
    return sensors


async def detect_motors() -> list[dict]:
    """Detect all connected motor devices (GPIO)."""
    hardware = await detect_all_hardware()
    return hardware["gpio"]


async def read_detected_sensor_status() -> list[dict]:
    """Read status from all detected sensors on the Pi."""
    sensors = await detect_sensors()
    results = []

    for dev in sensors:
        status = {
            "name": dev["name"],
            "online": dev["online"],
            "battery": 0,
            "signal": 0,
            "temperature": 0,
            "ping": 0,
            "interface": dev.get("interface", ""),
            "address": dev.get("address"),
        }

        if dev["interface"] == "I2C" and "MPU6050" in dev["name"]:
            try:
                addr = int(dev["address"], 16) if dev["address"] else 0x68
                from app.sensor.mpu6050 import MPU6050Sensor
                t0 = asyncio.get_event_loop().time()
                sens = MPU6050Sensor(bus_num=settings.I2C_BUS, address=addr)
                temp = await sens.read_temperature()
                ping_ms = round((asyncio.get_event_loop().time() - t0) * 1000, 1)
                status["temperature"] = temp
                status["ping"] = ping_ms
                status["signal"] = 100
            except Exception as e:
                logger.warning("Failed to read %s: %s", dev["name"], e)
                status["online"] = False

        results.append(status)

    return results


async def read_detected_motor_status() -> list[dict]:
    """Read status from all detected motor devices on the Pi."""
    motors = await detect_motors()
    results = []

    for dev in motors:
        results.append({
            "name": dev["name"],
            "online": True,
            "battery": 0,
            "signal": 0,
            "temperature": 0,
            "ping": 0,
            "interface": dev.get("interface", "GPIO"),
            "pin": dev.get("pin"),
        })

    return results
