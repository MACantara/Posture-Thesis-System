"""Hardware detection for Raspberry Pi 3 B+.

Scans I2C bus for connected sensors, checks GPIO availability for motors,
scans BLE for connected Bluetooth devices, and discovers devices on the
local network.
"""

import asyncio
import logging
import socket
import subprocess
import ipaddress

from app.config import settings

logger = logging.getLogger(__name__)

# Known I2C sensor addresses on the Pi 3 B+
KNOWN_I2C_DEVICES = {
    0x68: "MPU6050",
    0x69: "MPU6050 (alt addr)",
    0x76: "BME280",
    0x77: "BME280 (alt addr)",
    0x48: "ADS1115 (ADC for Flex Sensor)",
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


def _check_spi_devices() -> list[dict]:
    """Check for SPI-connected ADC devices (MCP3008)."""
    devices = []
    try:
        import spidev
        for bus in range(2):
            for dev in range(2):
                try:
                    spi = spidev.SpiDev()
                    spi.open(bus, dev)
                    # Try reading channel 0 — if it responds, MCP3008 is present
                    r = spi.xfer2([1, 0x80, 0])
                    val = ((r[1] & 3) << 8) + r[2]
                    devices.append({
                        "name": "MCP3008 SPI ADC",
                        "bus": bus,
                        "device": dev,
                        "interface": "SPI",
                        "channels": 8,
                    })
                    logger.info("MCP3008 detected on SPI bus %d device %d (ch0=%d)", bus, dev, val)
                    spi.close()
                    return devices  # Found one, no need to check more
                except Exception:
                    pass
    except ImportError:
        logger.debug("spidev not available — cannot scan SPI bus")
    except Exception as e:
        logger.debug("SPI scan failed: %s", e)
    return devices


def _detect_flex_sensor() -> dict | None:
    """Try to detect a flex sensor by initializing FlexSensor with auto-detection.

    The flex sensor is analog, so it won't appear on I2C/SPI bus scans directly.
    Instead, we check if any ADC (MCP3008, ADS1115, or GPIO RC) is available
    and can read data.
    """
    try:
        from app.sensor.flex_sensor import FlexSensor
        flex = FlexSensor(bus_num=settings.I2C_BUS)
        raw = flex._read_raw()
        adc_type = flex.adc_type
        return {
            "name": "Flex Sensor 4.5\" (SEN-08606)",
            "online": True,
            "interface": "Analog",
            "adc_type": adc_type,
            "raw_value": raw,
        }
    except Exception as e:
        logger.debug("Flex sensor not detected: %s", e)
        return None


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


def _get_local_network_info() -> dict:
    """Get the local machine's network interface info."""
    info = {"hostname": None, "ip_addresses": [], "network": None}
    try:
        info["hostname"] = socket.gethostname()
        hostname = socket.gethostname()
        try:
            local_ip = socket.gethostbyname(hostname)
            info["ip_addresses"].append(local_ip)
        except Exception:
            pass

        # Get all interfaces via hostname resolution
        try:
            all_addrs = socket.getaddrinfo(hostname, None)
            for addr in all_addrs:
                ip = addr[4][0]
                if ip not in info["ip_addresses"] and not ip.startswith("127."):
                    info["ip_addresses"].append(ip)
        except Exception:
            pass

        # Determine the local subnet from the first non-loopback IP
        for ip in info["ip_addresses"]:
            if ":" not in ip and not ip.startswith("127."):
                iface = ipaddress.ip_interface(f"{ip}/24")
                info["network"] = str(iface.network)
                break
    except Exception as e:
        logger.warning("Failed to get local network info: %s", e)
    return info


def _ping_host(ip: str, timeout: float = 1.0) -> bool:
    """Ping a single host and return True if reachable."""
    try:
        result = subprocess.run(
            ["ping", "-n", "1", "-w", str(int(timeout * 1000)), ip],
            capture_output=True, text=True, timeout=timeout + 1,
        )
        return result.returncode == 0
    except Exception:
        return False


def _check_port(ip: str, port: int, timeout: float = 1.0) -> bool:
    """Check if a TCP port is open on a host."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(timeout)
            return s.connect_ex((ip, port)) == 0
    except Exception:
        return False


async def _scan_network_devices() -> list[dict]:
    """Scan the local network for reachable devices.

    Pings all hosts in the /24 subnet and checks for common ports
    (22 SSH, 8000 FastAPI) to identify Raspberry Pi devices.
    """
    net_info = _get_local_network_info()
    network_str = net_info.get("network")

    if not network_str:
        logger.warning("Could not determine local network — skipping network scan")
        return []

    try:
        network = ipaddress.ip_network(network_str, strict=False)
    except Exception as e:
        logger.warning("Invalid network %s: %s", network_str, e)
        return []

    # Collect all hosts to scan (exclude network, broadcast, and our own IPs)
    own_ips = set(net_info["ip_addresses"])
    hosts = [str(ip) for ip in network.hosts() if str(ip) not in own_ips]

    logger.info("Scanning network %s (%d hosts)...", network_str, len(hosts))

    # Ping scan all hosts concurrently
    async def check_host(ip: str) -> dict | None:
        reachable = await asyncio.to_thread(_ping_host, ip, 0.5)
        if not reachable:
            return None

        device = {
            "ip": ip,
            "hostname": None,
            "online": True,
            "ports": {},
            "is_raspberry_pi": False,
        }

        # Try reverse DNS
        try:
            hostname = await asyncio.to_thread(socket.gethostbyaddr, ip)
            device["hostname"] = hostname[0]
        except Exception:
            pass

        # Check common ports
        for port, label in [(22, "ssh"), (8000, "api"), (80, "http"), (5173, "vite")]:
            open_port = await asyncio.to_thread(_check_port, ip, port, 0.5)
            if open_port:
                device["ports"][label] = port
                if port in (22, 8000):
                    device["is_raspberry_pi"] = True

        return device

    tasks = [check_host(ip) for ip in hosts]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    devices = [r for r in results if r is not None and not isinstance(r, Exception)]
    logger.info("Network scan complete: %d devices found", len(devices))
    return devices


async def detect_all_hardware() -> dict:
    """Detect all connected hardware on the Raspberry Pi.

    Returns a dict with 'i2c', 'spi', 'gpio', 'ble', 'flex', and 'network' lists.
    """
    i2c = await asyncio.to_thread(_scan_i2c_bus, settings.I2C_BUS)
    spi = await asyncio.to_thread(_check_spi_devices)
    gpio = await asyncio.to_thread(_check_gpio_pins)
    ble = await asyncio.to_thread(_scan_ble_devices)
    flex = await asyncio.to_thread(_detect_flex_sensor)
    network = await _scan_network_devices()

    return {
        "i2c": i2c,
        "spi": spi,
        "gpio": gpio,
        "ble": ble,
        "flex": flex,
        "network": network,
    }


async def detect_sensors() -> list[dict]:
    """Detect all connected sensors (I2C + SPI + BLE + Flex)."""
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
    for dev in hardware["spi"]:
        sensors.append({
            "name": dev["name"],
            "online": True,
            "interface": dev["interface"],
            "bus": dev.get("bus"),
            "device": dev.get("device"),
        })
    for dev in hardware["ble"]:
        sensors.append({
            "name": dev["name"],
            "online": True,
            "interface": dev["interface"],
            "address": dev.get("address"),
        })
    if hardware.get("flex"):
        sensors.append({
            "name": hardware["flex"]["name"],
            "online": True,
            "interface": hardware["flex"]["interface"],
            "adc_type": hardware["flex"].get("adc_type"),
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

        if "Flex Sensor" in dev["name"]:
            try:
                from app.sensor.flex_sensor import FlexSensor
                t0 = asyncio.get_event_loop().time()
                flex = FlexSensor(bus_num=settings.I2C_BUS)
                raw_data = await flex.read_raw_data()
                ping_ms = round((asyncio.get_event_loop().time() - t0) * 1000, 1)
                status["name"] = "Flex Sensor 4.5\" (SEN-08606)"
                status["temperature"] = 25.0
                status["ping"] = ping_ms
                status["signal"] = 100
                status["bend_angle"] = raw_data["bend_angle"]
                status["resistance"] = raw_data["resistance"]
                status["voltage"] = raw_data["voltage"]
                status["adc_type"] = flex.adc_type
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
