import asyncio
import json
import time

from app.sensor.mpu6050 import MPU6050Sensor


async def calibrate():
    print("MPU6050 Calibration Utility")
    print("=" * 40)
    print()

    try:
        sensor = MPU6050Sensor(bus_num=1)
    except Exception as e:
        print(f"Error: Could not initialize MPU6050: {e}")
        print("Make sure smbus2 is installed and the sensor is connected.")
        return

    print("Place the sensor flat and keep it still.")
    print("Collecting samples for 5 seconds...")
    print()

    accel_samples = {"x": [], "y": [], "z": []}
    gyro_samples = {"x": [], "y": [], "z": []}

    start = time.time()
    while time.time() - start < 5:
        ax, ay, az = await sensor.read_accel()
        gx, gy, gz = await sensor.read_gyro()
        accel_samples["x"].append(ax)
        accel_samples["y"].append(ay)
        accel_samples["z"].append(az)
        gyro_samples["x"].append(gx)
        gyro_samples["y"].append(gy)
        gyro_samples["z"].append(gz)
        await asyncio.sleep(0.1)

    def mean(lst):
        return round(sum(lst) / len(lst), 4) if lst else 0.0

    offsets = {
        "accel_x": mean(accel_samples["x"]),
        "accel_y": mean(accel_samples["y"]),
        "accel_z": mean(accel_samples["z"]) - 1.0,
        "gyro_x": mean(gyro_samples["x"]),
        "gyro_y": mean(gyro_samples["y"]),
        "gyro_z": mean(gyro_samples["z"]),
    }

    print("Calibration complete!")
    print()
    print("Calibration offsets:")
    print(json.dumps(offsets, indent=2))
    print()
    print("Save these to your .env file as CALIBRATION_OFFSETS:")
    print(f'CALIBRATION_OFFSETS={json.dumps(offsets)}')
    print()
    print("Or use these values in the MPU6050Sensor constructor.")


if __name__ == "__main__":
    asyncio.run(calibrate())
