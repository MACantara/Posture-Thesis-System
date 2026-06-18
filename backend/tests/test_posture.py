import pytest


@pytest.mark.asyncio
async def test_get_records(client, auth_headers):
    response = await client.get("/api/posture/records", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_records_with_status_filter(client, auth_headers):
    response = await client.get("/api/posture/records?status=good", headers=auth_headers)
    assert response.status_code == 200
    records = response.json()
    for r in records:
        assert r["status"] == "good"


@pytest.mark.asyncio
async def test_get_records_pagination(client, auth_headers):
    response = await client.get("/api/posture/records?limit=5&offset=0", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) <= 5


@pytest.mark.asyncio
async def test_get_stats(client, auth_headers):
    response = await client.get("/api/posture/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_sessions" in data
    assert "good_posture_count" in data
    assert "average_angle" in data
    assert "improvement_rate" in data


@pytest.mark.asyncio
async def test_create_record(client, auth_headers):
    response = await client.post("/api/posture/records", headers=auth_headers, json={
        "status": "good",
        "angle": 5.2,
        "duration": 10.0,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "good"
    assert data["angle"] == 5.2


@pytest.mark.asyncio
async def test_records_without_auth(client):
    response = await client.get("/api/posture/records")
    assert response.status_code == 401
