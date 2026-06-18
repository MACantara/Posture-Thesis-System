# Hardware Integration

## Supported Hardware

| Component | Model | Interface | Pin |
|-----------|-------|-----------|-----|
| IMU Sensor | MPU6050 | I2C (bus 1) | SDA: GPIO2, SCL: GPIO3 |
| Servo Motor | SG90 | PWM | GPIO18 |
| Vibrator | DC motor | GPIO | GPIO23 |

## Wiring (Raspberry Pi 3 B+)

### MPU6050 (I2C)
```
MPU6050 VCC → Pi 3.3V (Pin 1)
MPU6050 GND → Pi GND (Pin 6)
MPU6050 SDA → Pi GPIO2 (Pin 3)
MPU6050 SCL → Pi GPIO3 (Pin 5)
```

### Servo Motor (PWM)
```
Servo VCC  → Pi 5V (Pin 2)
Servo GND  → Pi GND (Pin 6)
Servo Signal → Pi GPIO18 (Pin 12)
```

## Software Setup

### 1. Enable I2C on Raspberry Pi
```bash
sudo raspi-config
# Interface Options → I2C → Enable
```

### 2. Install hardware dependencies
```bash
pip install smbus2 RPi.GPIO
```

### 3. Switch from mock to hardware
Edit `.env`:
```
USE_MOCK_SENSORS=False
```

### 4. Calibrate the sensor
```bash
cd backend
python -m app.sensor.calibration
```
Follow the prompts, then save the output offsets to your `.env` file.

## Plug-and-Play Architecture

The sensor factory (`app/sensor/factory.py`) automatically detects hardware availability:

- If `USE_MOCK_SENSORS=True` → uses mock sensors
- If `USE_MOCK_SENSORS=False` → tries to import hardware drivers
- If hardware drivers unavailable → falls back to mock with a warning

This allows seamless development on any machine and deployment on Pi without code changes.

## Calibration

The MPU6050 calibration utility (`app/sensor/calibration.py`):
1. Collects 5 seconds of sensor data while flat
2. Computes average offsets for accel and gyro
3. Outputs JSON to save in `.env` as `CALIBRATION_OFFSETS`

## Posture Detection Thresholds

Configurable via environment variables:
- `POSTURE_ANGLE_THRESHOLD_GOOD` (default: 10°) — Below this = good posture
- `POSTURE_ANGLE_THRESHOLD_WARNING` (default: 20°) — Below this = warning
- Above warning threshold = poor posture
