import logging

from app.config import settings
from app.sensor.interfaces import SensorInterface, MotorInterface

logger = logging.getLogger(__name__)


def get_sensor() -> SensorInterface:
    """Initialize sensor from detected I2C devices on the Pi."""
    try:
        from app.sensor.mpu6050 import MPU6050Sensor, HAS_SMBUS
        if not HAS_SMBUS:
            raise RuntimeError("smbus2 not available — cannot access I2C bus")

        # Try configured address first, then scan common MPU6050 addresses
        addresses_to_try = [settings.MPU6050_ADDRESS, 0x68, 0x69]
        seen = set()
        for addr in addresses_to_try:
            if addr in seen:
                continue
            seen.add(addr)
            try:
                import smbus2
                bus = smbus2.SMBus(settings.I2C_BUS)
                bus.read_byte(addr)
                bus.close()
                logger.info("MPU6050 detected at address 0x%02X", addr)
                return MPU6050Sensor(bus_num=settings.I2C_BUS, address=addr)
            except (OSError, IOError):
                continue

        raise RuntimeError("No MPU6050 sensor detected on I2C bus — check wiring and I2C enablement")
    except RuntimeError:
        raise
    except Exception as e:
        raise RuntimeError(f"Hardware sensor not available: {e}")


def get_motor() -> MotorInterface:
    """Initialize motor from detected GPIO pins on the Pi."""
    try:
        from app.sensor.servo import ServoMotor
        return ServoMotor(pin=settings.SERVO_GPIO_PIN)
    except Exception as e:
        raise RuntimeError(f"Hardware motor not available: {e}")

