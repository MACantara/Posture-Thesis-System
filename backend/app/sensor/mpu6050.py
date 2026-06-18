import math
import time
import logging

from app.sensor.interfaces import SensorInterface

logger = logging.getLogger(__name__)

try:
    import smbus2
    HAS_SMBUS = True
except ImportError:
    HAS_SMBUS = False
    logger.warning("smbus2 not installed — MPU6050 hardware sensor unavailable")


class MPU6050Sensor(SensorInterface):
    I2C_ADDR = 0x68

    PWR_MGMT_1 = 0x6B
    ACCEL_XOUT_H = 0x3B
    ACCEL_YOUT_H = 0x3D
    ACCEL_ZOUT_H = 0x3F
    GYRO_XOUT_H = 0x43
    GYRO_YOUT_H = 0x45
    GYRO_ZOUT_H = 0x47
    TEMP_OUT_H = 0x41

    ACCEL_SCALE = 16384.0
    GYRO_SCALE = 131.0

    def __init__(self, bus_num: int = 1, calibration_offsets: dict | None = None):
        if not HAS_SMBUS:
            raise RuntimeError("smbus2 not available — cannot initialize MPU6050")

        self.bus = smbus2.SMBus(bus_num)
        self.bus.write_byte_data(self.I2C_ADDR, self.PWR_MGMT_1, 0)

        self._calibration = calibration_offsets or {
            "accel_x": 0.0, "accel_y": 0.0, "accel_z": 0.0,
            "gyro_x": 0.0, "gyro_y": 0.0, "gyro_z": 0.0,
        }
        self._baseline_angle = 0.0
        self._last_time = time.time()
        self._gyro_integral = [0.0, 0.0, 0.0]

        logger.info("MPU6050 initialized on I2C bus %d", bus_num)

    def _read_word(self, reg: int) -> int:
        high = self.bus.read_byte_data(self.I2C_ADDR, reg)
        low = self.bus.read_byte_data(self.I2C_ADDR, reg + 1)
        val = (high << 8) + low
        if val >= 0x8000:
            val -= 0x10000
        return val

    def recalibrate(self) -> None:
        self._baseline_angle = 0.0
        self._gyro_integral = [0.0, 0.0, 0.0]
        logger.info("MPU6050 recalibrated")

    async def read_accel(self) -> tuple[float, float, float]:
        x = self._read_word(self.ACCEL_XOUT_H) / self.ACCEL_SCALE - self._calibration["accel_x"]
        y = self._read_word(self.ACCEL_YOUT_H) / self.ACCEL_SCALE - self._calibration["accel_y"]
        z = self._read_word(self.ACCEL_ZOUT_H) / self.ACCEL_SCALE - self._calibration["accel_z"]
        return (round(x, 4), round(y, 4), round(z, 4))

    async def read_gyro(self) -> tuple[float, float, float]:
        x = self._read_word(self.GYRO_XOUT_H) / self.GYRO_SCALE - self._calibration["gyro_x"]
        y = self._read_word(self.GYRO_YOUT_H) / self.GYRO_SCALE - self._calibration["gyro_y"]
        z = self._read_word(self.GYRO_ZOUT_H) / self.GYRO_SCALE - self._calibration["gyro_z"]
        return (round(x, 2), round(y, 2), round(z, 2))

    async def read_temperature(self) -> float:
        raw = self._read_word(self.TEMP_OUT_H)
        temp = raw / 340.0 + 36.53
        return round(temp, 2)

    async def get_posture_angle(self) -> float:
        ax, ay, az = await self.read_accel()
        accel_angle = math.degrees(math.atan2(ax, math.sqrt(ay**2 + az**2)))

        now = time.time()
        dt = now - self._last_time
        self._last_time = now

        gx, gy, gz = await self.read_gyro()
        self._gyro_integral[0] += gx * dt
        self._gyro_integral[1] += gy * dt
        self._gyro_integral[2] += gz * dt

        angle = 0.98 * (self._gyro_integral[0] + self._baseline_angle) + 0.02 * accel_angle
        return round(abs(angle), 2)
