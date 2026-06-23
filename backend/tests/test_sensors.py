import pytest


@pytest.mark.asyncio
async def test_sensors_without_auth(client):
    response = await client.get("/api/sensors/status")
    assert response.status_code == 401
