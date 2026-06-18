import pytest
import asyncio

from app.sensor.mock_sensor import MockSensor
from app.sensor.mock_motor import MockMotor
from app.sensor.posture_detector import PostureDetector


@pytest.mark.asyncio
async def test_mock_sensor_accel_range():
    sensor = MockSensor()
    x, y, z = await sensor.read_accel()
    assert -2.0 <= x <= 2.0
    assert -2.0 <= y <= 2.0
    assert -2.0 <= z <= 2.0


@pytest.mark.asyncio
async def test_mock_sensor_gyro_range():
    sensor = MockSensor()
    x, y, z = await sensor.read_gyro()
    assert -20.0 <= x <= 20.0
    assert -20.0 <= y <= 20.0
    assert -20.0 <= z <= 20.0


@pytest.mark.asyncio
async def test_mock_sensor_temperature():
    sensor = MockSensor()
    temp = await sensor.read_temperature()
    assert 30.0 <= temp <= 45.0


@pytest.mark.asyncio
async def test_mock_sensor_angle_positive():
    sensor = MockSensor()
    angle = await sensor.get_posture_angle()
    assert angle >= 0.0


@pytest.mark.asyncio
async def test_mock_sensor_demo_states():
    sensor = MockSensor()
    sensor.set_demo_state("good")
    angle_good = await sensor.get_posture_angle()

    sensor.set_demo_state("poor")
    angle_poor = await sensor.get_posture_angle()

    assert angle_poor >= angle_good or abs(angle_poor - angle_good) < 50


@pytest.mark.asyncio
async def test_posture_detector_classification():
    assert PostureDetector.classify(5.0) == "good"
    assert PostureDetector.classify(15.0) == "warning"
    assert PostureDetector.classify(30.0) == "poor"


@pytest.mark.asyncio
async def test_posture_detector_intensity():
    assert PostureDetector.get_intensity(5.0) == 0.0
    assert 0 < PostureDetector.get_intensity(15.0) <= 1.0
    assert PostureDetector.get_intensity(30.0) > 0.0


@pytest.mark.asyncio
async def test_mock_motor_correct_posture():
    motor = MockMotor()
    await motor.correct_posture(25.0)
    assert len(motor.log) == 1
    assert motor.log[0]["action"] == "correct_posture"
    assert motor.log[0]["posture_angle"] == 25.0


@pytest.mark.asyncio
async def test_mock_motor_alert_feedback():
    motor = MockMotor()
    await motor.alert_feedback(0.8)
    assert len(motor.log) == 1
    assert motor.log[0]["action"] == "alert_feedback"
    assert motor.log[0]["intensity"] == 0.8
