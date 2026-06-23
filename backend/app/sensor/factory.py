import logging

from app.sensor.interfaces import SensorInterface, MotorInterface

logger = logging.getLogger(__name__)


def get_sensor() -> SensorInterface:
    try:
        from app.sensor.mpu6050 import MPU6050Sensor
        return MPU6050Sensor()
    except Exception as e:
        raise RuntimeError(f"Hardware sensor not available: {e}")


def get_motor() -> MotorInterface:
    try:
        from app.sensor.servo import ServoMotor
        return ServoMotor()
    except Exception as e:
        raise RuntimeError(f"Hardware motor not available: {e}")

