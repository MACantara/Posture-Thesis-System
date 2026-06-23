import pytest

from app.sensor.posture_detector import PostureDetector


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
