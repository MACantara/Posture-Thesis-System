import pytest


@pytest.mark.asyncio
async def test_get_sensor_status(client, auth_headers):
    response = await client.get("/api/sensors/status", headers=auth_headers)
    assert response.status_code == 200
    sensors = response.json()
    assert isinstance(sensors, list)
    assert len(sensors) > 0
    sensor = sensors[0]
    assert "name" in sensor
    assert "online" in sensor
    assert "battery" in sensor
    assert "signal" in sensor
    assert "temperature" in sensor
    assert "ping" in sensor


@pytest.mark.asyncio
async def test_sensors_without_auth(client):
    response = await client.get("/api/sensors/status")
    assert response.status_code == 401
