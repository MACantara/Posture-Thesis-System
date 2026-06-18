from app.sensor.interfaces import MotorInterface


class MockMotor(MotorInterface):
    def __init__(self):
        self._log: list[dict] = []

    async def correct_posture(self, angle: float) -> None:
        servo_angle = min(max(angle * 3, 0), 180)
        entry = {
            "action": "correct_posture",
            "posture_angle": angle,
            "servo_angle": round(servo_angle, 2),
        }
        self._log.append(entry)
        print(f"[MockMotor] correct_posture: angle={angle}°, servo={servo_angle}°")

    async def alert_feedback(self, intensity: float) -> None:
        duration = min(max(intensity * 2, 0.5), 2.0)
        entry = {
            "action": "alert_feedback",
            "intensity": intensity,
            "duration": round(duration, 2),
        }
        self._log.append(entry)
        print(f"[MockMotor] alert_feedback: intensity={intensity}, duration={duration}s")

    @property
    def log(self) -> list[dict]:
        return self._log
