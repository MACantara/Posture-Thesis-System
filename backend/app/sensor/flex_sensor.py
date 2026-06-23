"""Flex Sensor 4.5" (SparkFun SEN-08606) driver for Raspberry Pi.

The flex sensor is an analog resistance sensor — resistance increases
as it bends. It requires an ADC to read on the Pi (which lacks analog inputs).

Default setup: ADS1115 ADC on I2C address 0x48, flex sensor on channel A0
via voltage divider circuit.

Voltage divider:
  VCC --- [Flex Sensor] ---+--- [10k resistor] --- GND
                            |
                          ADC input (A0)

As the sensor bends, resistance increases, voltage at the divider
midpoint changes, and the ADC reads the difference.
"""

import logging
import time

logger = logging.getLogger(__name__)

try:
    import smbus2
    HAS_SMBUS = True
except ImportError:
    HAS_SMBUS = False
    logger.warning("smbus2 not installed — FlexSensor hardware unavailable")


class FlexSensor:
    """SparkFun Flex Sensor 4.5" via ADS1115 ADC.

    Reads analog voltage from the flex sensor through an ADS1115 ADC
    and converts it to a bend angle.
    """

    # ADS1115 registers
    ADS1115_REG_POINTER = 0x00
    ADS1115_REG_CONFIG = 0x01

    # ADS1115 config: single-shot, A0, gain 4.096V, 128 SPS
    # Config bits: OS=1, MUX=100 (A0), PGA=010 (4.096V), MODE=1 (single-shot),
    #              DR=100 (128 SPS), COMP modes=0
    ADS1115_CONFIG_SINGLE_SHOT_A0 = 0xC103
    ADS1115_CONFIG_SINGLE_SHOT_A1 = 0xD103
    ADS1115_CONFIG_SINGLE_SHOT_A2 = 0xE103
    ADS1115_CONFIG_SINGLE_SHOT_A3 = 0xF103

    # Voltage divider parameters
    VCC = 3.3
    DIVIDER_R = 10000.0  # 10k ohm fixed resistor

    # Flex sensor resistance range (approximate, from datasheet)
    FLEX_FLAT_R = 25000.0    # ~25k ohm when flat
    FLEX_BENT_R = 100000.0   # ~100k ohm when fully bent

    def __init__(
        self,
        bus_num: int = 1,
        address: int = 0x48,
        channel: int = 0,
        flat_calibration: float | None = None,
        bent_calibration: float | None = None,
    ):
        if not HAS_SMBUS:
            raise RuntimeError("smbus2 not available — cannot initialize FlexSensor")

        self.bus = smbus2.SMBus(bus_num)
        self.address = address
        self.channel = channel
        self._baseline_angle = 0.0

        # Calibration values (raw ADC readings at flat and bent positions)
        self._flat_cal = flat_calibration
        self._bent_cal = bent_calibration

        # Auto-calibrate flat position on init if no calibration provided
        if self._flat_cal is None:
            try:
                self._flat_cal = self._read_raw()
                logger.info("FlexSensor auto-calibrated flat: raw=%d", self._flat_cal)
            except Exception:
                self._flat_cal = 0

        if self._bent_cal is None:
            # Estimate bent calibration from voltage divider math
            self._bent_cal = self._flat_cal + 12000  # approximate range

        logger.info(
            "FlexSensor initialized: addr=0x%02X channel=%d flat_cal=%d bent_cal=%d",
            address, channel, self._flat_cal, self._bent_cal,
        )

    def _read_raw(self) -> int:
        """Read raw ADC value from the configured channel."""
        config_map = {
            0: self.ADS1115_CONFIG_SINGLE_SHOT_A0,
            1: self.ADS1115_CONFIG_SINGLE_SHOT_A1,
            2: self.ADS1115_CONFIG_SINGLE_SHOT_A2,
            3: self.ADS1115_CONFIG_SINGLE_SHOT_A3,
        }
        config = config_map.get(self.channel, self.ADS1115_CONFIG_SINGLE_SHOT_A0)

        # Write config to start conversion
        self.bus.write_i2c_block_data(
            self.address,
            self.ADS1115_REG_CONFIG,
            [(config >> 8) & 0xFF, config & 0xFF],
        )

        # Wait for conversion (128 SPS ~ 8ms)
        time.sleep(0.01)

        # Read conversion result
        data = self.bus.read_i2c_block_data(self.address, self.ADS1115_REG_POINTER, 2)
        raw = (data[0] << 8) | data[1]

        # Convert to signed 16-bit
        if raw >= 0x8000:
            raw -= 0x10000

        return raw

    def read_voltage(self) -> float:
        """Read the voltage at the flex sensor divider midpoint."""
        raw = self._read_raw()
        # ADS1115 with PGA=4.096V: 16-bit signed, full scale = 4.096V
        voltage = raw * 4.096 / 32767.0
        return round(voltage, 4)

    def read_resistance(self) -> float:
        """Calculate flex sensor resistance from voltage divider.

        V_divider = VCC * R_fixed / (R_flex + R_fixed)
        R_flex = R_fixed * (VCC / V_divider - 1)
        """
        voltage = self.read_voltage()
        if voltage <= 0:
            return self.FLEX_BENT_R
        resistance = self.DIVIDER_R * (self.VCC / voltage - 1)
        return round(resistance, 1)

    def read_bend_angle(self) -> float:
        """Convert raw ADC reading to bend angle in degrees.

        Maps the raw ADC range (flat to bent) to 0-90 degrees.
        0° = flat, 90° = fully bent.
        """
        raw = self._read_raw()
        raw_range = self._bent_cal - self._flat_cal
        if raw_range == 0:
            return 0.0

        angle = (raw - self._flat_cal) / raw_range * 90.0
        angle = max(0.0, min(90.0, angle))
        return round(angle, 2)

    def recalibrate(self) -> None:
        """Recalibrate the flat (neutral) position."""
        self._flat_cal = self._read_raw()
        self._baseline_angle = 0.0
        logger.info("FlexSensor recalibrated: flat_cal=%d", self._flat_cal)

    def recalibrate_bent(self) -> None:
        """Calibrate the fully bent position."""
        self._bent_cal = self._read_raw()
        logger.info("FlexSensor bent calibrated: bent_cal=%d", self._bent_cal)

    async def read_accel(self) -> tuple[float, float, float]:
        """Flex sensor has no accelerometer — return zeros."""
        return (0.0, 0.0, 0.0)

    async def read_gyro(self) -> tuple[float, float, float]:
        """Flex sensor has no gyroscope — return zeros."""
        return (0.0, 0.0, 0.0)

    async def read_temperature(self) -> float:
        """Flex sensor has no temperature — return ambient estimate."""
        return 25.0

    async def get_posture_angle(self) -> float:
        """Get posture angle from flex sensor bend.

        Returns the bend angle relative to the calibrated neutral position.
        This directly represents posture deviation.
        """
        angle = self.read_bend_angle()
        posture_angle = abs(angle - self._baseline_angle)
        return round(posture_angle, 2)

    async def read_raw_data(self) -> dict:
        """Read all raw data from the flex sensor."""
        return {
            "raw_adc": self._read_raw(),
            "voltage": self.read_voltage(),
            "resistance": self.read_resistance(),
            "bend_angle": self.read_bend_angle(),
        }
