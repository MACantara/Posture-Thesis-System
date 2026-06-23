"""Flex Sensor 4.5" (SparkFun SEN-08606) driver for Raspberry Pi 3 B+.

The flex sensor is an analog variable resistor — resistance increases
as it bends. The Pi 3 B+ has no analog inputs, so an ADC is required.

Supports three ADC types (auto-detected in priority order):
  1. MCP3008 — SPI ADC, 10-bit, 8 channels (most common with Pi)
  2. ADS1115 — I2C ADC, 16-bit, 4 channels (address 0x48)
  3. GPIO RC circuit — no ADC, uses capacitor charge timing on a GPIO pin

Voltage divider circuit (per SparkFun hookup guide):
  3.3V --- [Flex Sensor] ---+--- [47kΩ resistor] --- GND
                             |
                           ADC input (CH0)

As the sensor bends, resistance increases (30kΩ flat → 70kΩ at 90°),
voltage at the divider midpoint decreases, and the ADC reads lower values.

Datasheet values (SpectraSymbol FS7548):
  Flat resistance: ~10kΩ (datasheet) / ~30kΩ (observed, 4.5" sensor)
  Bend resistance: 60k-110kΩ (datasheet) / ~70kΩ at 90° (observed)
  Resistance tolerance: ±30%
  Power rating: 0.50W continuous, 1W peak
  Temperature range: -35°C to +80°C
  Life cycle: >1 million
"""

import logging
import time

from app.config import settings

logger = logging.getLogger(__name__)

try:
    import smbus2
    HAS_SMBUS = True
except ImportError:
    HAS_SMBUS = False

try:
    import spidev
    HAS_SPI = True
except ImportError:
    HAS_SPI = False

try:
    import RPi.GPIO as GPIO
    HAS_GPIO = True
except ImportError:
    HAS_GPIO = False


class FlexSensor:
    """SparkFun Flex Sensor 4.5" (SEN-08606) via ADC.

    Auto-detects and uses the first available ADC:
      1. MCP3008 (SPI, 10-bit, 0-1023)
      2. ADS1115 (I2C, 16-bit, signed)
      3. GPIO RC circuit (no ADC, timing-based)

    Voltage divider (per hookup guide):
      3.3V --- [Flex Sensor] ---+--- [47kΩ resistor] --- GND
                                 |
                               ADC input
    As flex resistance increases (bending), voltage at ADC decreases.
    """

    # ADS1115 registers
    ADS1115_REG_POINTER = 0x00
    ADS1115_REG_CONFIG = 0x01
    ADS1115_CONFIG_BASE = 0xC103  # single-shot, PGA=4.096V, 128 SPS

    # Voltage divider parameters (per SparkFun hookup guide)
    VCC = 3.3
    DIVIDER_R = 47000.0  # 47kΩ recommended in hookup guide

    # Flex sensor resistance range (from datasheet + hookup guide)
    FLEX_FLAT_R = 30000.0   # ~30kΩ when flat (hookup guide)
    FLEX_BENT_R = 70000.0   # ~70kΩ at 90° bend (hookup guide)

    # ADC type identifiers
    ADC_MCP3008 = "mcp3008"
    ADC_ADS1115 = "ads1115"
    ADC_GPIO_RC = "gpio_rc"

    def __init__(
        self,
        bus_num: int = 1,
        address: int = 0x48,
        channel: int = 0,
        adc_type: str | None = None,
        spi_bus: int = 0,
        spi_device: int = 0,
        gpio_pin: int = 4,
        flat_calibration: float | None = None,
        bent_calibration: float | None = None,
    ):
        self.channel = channel
        self._baseline_angle = 0.0
        self._flat_cal = flat_calibration
        self._bent_cal = bent_calibration
        self.adc_type = None
        self.bus = None
        self.spi = None
        self.gpio_pin = gpio_pin

        # Auto-detect ADC if not specified
        if adc_type:
            self._init_adc(adc_type, bus_num, address, spi_bus, spi_device)
        else:
            self._auto_detect_adc(bus_num, address, spi_bus, spi_device)

        if self.adc_type is None:
            raise RuntimeError(
                "No ADC available for FlexSensor. Ensure MCP3008 (SPI), "
                "ADS1115 (I2C 0x48), or GPIO RC circuit is connected."
            )

        # Auto-calibrate flat position on init if no calibration provided
        if self._flat_cal is None:
            try:
                self._flat_cal = self._read_raw()
                logger.info("FlexSensor auto-calibrated flat: raw=%d", self._flat_cal)
            except Exception:
                self._flat_cal = 0

        if self._bent_cal is None:
            # Estimate bent calibration based on ADC type
            if self.adc_type == self.ADC_MCP3008:
                # 10-bit: flat ~ high value, bent ~ lower value
                flat_voltage = self.VCC * self.DIVIDER_R / (self.FLEX_FLAT_R + self.DIVIDER_R)
                bent_voltage = self.VCC * self.DIVIDER_R / (self.FLEX_BENT_R + self.DIVIDER_R)
                self._bent_cal = int(bent_voltage / self.VCC * 1023)
            elif self.adc_type == self.ADC_ADS1115:
                flat_voltage = self.VCC * self.DIVIDER_R / (self.FLEX_FLAT_R + self.DIVIDER_R)
                bent_voltage = self.VCC * self.DIVIDER_R / (self.FLEX_BENT_R + self.DIVIDER_R)
                self._bent_cal = int(bent_voltage / 4.096 * 32767)
            else:
                self._bent_cal = self._flat_cal * 2  # rough estimate for RC

        logger.info(
            "FlexSensor initialized: adc=%s channel=%d flat_cal=%d bent_cal=%d",
            self.adc_type, self.channel, self._flat_cal, self._bent_cal,
        )

    def _auto_detect_adc(self, bus_num: int, address: int, spi_bus: int, spi_device: int):
        """Try each ADC type in priority order."""
        # Try MCP3008 (SPI) first — most common with Pi
        if HAS_SPI:
            try:
                self._init_mcp3008(spi_bus, spi_device)
                return
            except Exception as e:
                logger.debug("MCP3008 not available: %s", e)

        # Try ADS1115 (I2C)
        if HAS_SMBUS:
            try:
                self._init_ads1115(bus_num, address)
                return
            except Exception as e:
                logger.debug("ADS1115 not available: %s", e)

        # Try GPIO RC circuit (no ADC needed)
        if HAS_GPIO:
            try:
                self._init_gpio_rc()
                return
            except Exception as e:
                logger.debug("GPIO RC not available: %s", e)

    def _init_adc(self, adc_type: str, bus_num: int, address: int, spi_bus: int, spi_device: int):
        if adc_type == self.ADC_MCP3008:
            self._init_mcp3008(spi_bus, spi_device)
        elif adc_type == self.ADC_ADS1115:
            self._init_ads1115(bus_num, address)
        elif adc_type == self.ADC_GPIO_RC:
            self._init_gpio_rc()
        else:
            raise RuntimeError(f"Unknown ADC type: {adc_type}")

    def _init_mcp3008(self, spi_bus: int, spi_device: int):
        """Initialize MCP3008 SPI ADC."""
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = 1350000
        self.spi.mode = 0
        self.adc_type = self.ADC_MCP3008
        logger.info("MCP3008 SPI ADC initialized: bus=%d device=%d", spi_bus, spi_device)

    def _init_ads1115(self, bus_num: int, address: int):
        """Initialize ADS1115 I2C ADC."""
        self.bus = smbus2.SMBus(bus_num)
        self.address = address
        # Verify device responds
        self.bus.read_byte(address)
        self.adc_type = self.ADC_ADS1115
        logger.info("ADS1115 I2C ADC initialized: bus=%d addr=0x%02X", bus_num, address)

    def _init_gpio_rc(self):
        """Initialize GPIO for RC timing circuit (no ADC needed).

        RC circuit:
          GPIO pin --- [Flex Sensor] --- 0.1µF cap --- GND
        Measure time to charge capacitor through flex sensor resistance.
        """
        GPIO.setmode(GPIO.BCM)
        self.adc_type = self.ADC_GPIO_RC
        logger.info("GPIO RC circuit initialized on pin %d", self.gpio_pin)

    def _read_mcp3008(self, channel: int) -> int:
        """Read from MCP3008 SPI ADC (10-bit, 0-1023)."""
        if channel < 0 or channel > 7:
            raise ValueError("MCP3008 channel must be 0-7")
        # MCP3008 command: start bit, single-ended mode, channel
        r = self.spi.xfer2([1, (8 + channel) << 4, 0])
        return ((r[1] & 3) << 8) + r[2]

    def _read_ads1115(self, channel: int) -> int:
        """Read from ADS1115 I2C ADC (16-bit signed)."""
        config = self.ADS1115_CONFIG_BASE | (channel << 12)
        self.bus.write_i2c_block_data(
            self.address,
            self.ADS1115_REG_CONFIG,
            [(config >> 8) & 0xFF, config & 0xFF],
        )
        time.sleep(0.01)
        data = self.bus.read_i2c_block_data(self.address, self.ADS1115_REG_POINTER, 2)
        raw = (data[0] << 8) | data[1]
        if raw >= 0x8000:
            raw -= 0x10000
        return raw

    def _read_gpio_rc(self) -> int:
        """Read via GPIO RC timing circuit.

        Measures capacitor charge time through flex sensor resistance.
        Higher resistance = longer charge time = more bend.
        Returns a timing count proportional to resistance.
        """
        GPIO.setup(self.gpio_pin, GPIO.OUT)
        GPIO.output(self.gpio_pin, GPIO.LOW)
        time.sleep(0.01)
        GPIO.setup(self.gpio_pin, GPIO.IN)
        count = 0
        while GPIO.input(self.gpio_pin) == GPIO.LOW:
            count += 1
            if count > 100000:
                break
        return count

    def _read_raw(self) -> int:
        """Read raw ADC value from the configured channel."""
        if self.adc_type == self.ADC_MCP3008:
            return self._read_mcp3008(self.channel)
        elif self.adc_type == self.ADC_ADS1115:
            return self._read_ads1115(self.channel)
        elif self.adc_type == self.ADC_GPIO_RC:
            return self._read_gpio_rc()
        else:
            raise RuntimeError("No ADC initialized")

    def read_voltage(self) -> float:
        """Read the voltage at the flex sensor divider midpoint."""
        raw = self._read_raw()
        if self.adc_type == self.ADC_MCP3008:
            voltage = raw * self.VCC / 1023.0
        elif self.adc_type == self.ADC_ADS1115:
            voltage = raw * 4.096 / 32767.0
        else:
            # GPIO RC: no direct voltage, estimate from timing
            voltage = min(raw / 10000.0 * self.VCC, self.VCC)
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
