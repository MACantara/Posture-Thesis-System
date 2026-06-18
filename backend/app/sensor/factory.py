from app.config import settings
from app.sensor.interfaces import SensorInterface, MotorInterface
from app.sensor.mock_sensor import MockSensor
from app.sensor.mock_motor import MockMotor


def get_sensor() -> SensorInterface:
    if settings.USE_MOCK_SENSORS:
        return MockSensor()
    try:
        from app.sensor.mpu6050 import MPU6050Sensor
        return MPU6050Sensor()
    except Exception:
        import logging
        logging.warning("Hardware sensor not available, falling back to mock.")
        return MockSensor()


def get_motor() -> MotorInterface:
    if settings.USE_MOCK_SENSORS:
        return MockMotor()
    try:
        from app.sensor.servo import ServoMotor
        return ServoMotor()
    except Exception:
        import logging
        logging.warning("Hardware motor not available, falling back to mock.")
        return MockMotor()
