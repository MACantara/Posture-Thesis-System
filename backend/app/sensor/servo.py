import logging

from app.sensor.interfaces import MotorInterface

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
    HAS_GPIO = True
except ImportError:
    HAS_GPIO = False
    logger.warning("RPi.GPIO not installed — servo motor hardware unavailable")


class ServoMotor(MotorInterface):
    def __init__(self, pin: int = 18, freq: int = 50):
        if not HAS_GPIO:
            raise RuntimeError("RPi.GPIO not available — cannot initialize servo")

        self.pin = pin
        self.freq = freq
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin, self.freq)
        self.pwm.start(0)
        logger.info("Servo motor initialized on GPIO pin %d", pin)

    def _set_angle(self, angle: float) -> None:
        duty = 2.5 + (angle / 180.0) * 10.0
        self.pwm.ChangeDutyCycle(duty)

    async def correct_posture(self, angle: float) -> None:
        servo_angle = min(max(angle * 3, 0), 180)
        self._set_angle(servo_angle)
        logger.info("Servo correct_posture: posture=%.1f°, servo=%.1f°", angle, servo_angle)

    async def alert_feedback(self, intensity: float) -> None:
        duty = min(max(intensity * 12, 3), 12)
        self.pwm.ChangeDutyCycle(duty)

    def cleanup(self) -> None:
        self.pwm.stop()
        GPIO.cleanup(self.pin)
