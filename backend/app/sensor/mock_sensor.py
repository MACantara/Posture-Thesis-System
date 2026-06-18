import random
import math
import time

from app.sensor.interfaces import SensorInterface


class MockSensor(SensorInterface):
    def __init__(self):
        self._demo_state: str = "good"
        self._baseline_angle: float = 0.0
        self._last_gyro_time: float = time.time()
        self._gyro_integral: tuple[float, float, float] = (0.0, 0.0, 0.0)

    def set_demo_state(self, state: str) -> None:
        if state in ("good", "warning", "poor"):
            self._demo_state = state

    def recalibrate(self) -> None:
        self._baseline_angle = 0.0
        self._gyro_integral = (0.0, 0.0, 0.0)

    async def read_accel(self) -> tuple[float, float, float]:
        noise = lambda: random.gauss(0, 0.05)

        if self._demo_state == "good":
            return (noise(), noise(), 1.0 + noise())
        elif self._demo_state == "warning":
            return (0.15 + noise(), noise(), 0.99 + noise())
        else:
            return (0.35 + noise(), 0.05 + noise(), 0.95 + noise())

    async def read_gyro(self) -> tuple[float, float, float]:
        noise = lambda: random.gauss(0, 0.5)

        if self._demo_state == "good":
            return (noise(), noise(), noise())
        elif self._demo_state == "warning":
            return (2.0 + noise(), noise(), noise())
        else:
            return (5.0 + noise(), noise(), noise())

    async def read_temperature(self) -> float:
        return round(36.5 + random.gauss(0, 0.2), 2)

    async def get_posture_angle(self) -> float:
        accel_x, accel_y, accel_z = await self.read_accel()
        accel_angle = math.degrees(math.atan2(accel_x, math.sqrt(accel_y**2 + accel_z**2)))

        now = time.time()
        dt = now - self._last_gyro_time
        self._last_gyro_time = now

        gyro_x, gyro_y, gyro_z = await self.read_gyro()
        gx, gy, gz = self._gyro_integral
        self._gyro_integral = (gx + gyro_x * dt, gy + gyro_y * dt, gz + gyro_z * dt)

        angle = 0.98 * (self._gyro_integral[0] + self._baseline_angle) + 0.02 * accel_angle
        return round(abs(angle), 2)
