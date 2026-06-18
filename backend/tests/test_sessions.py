import pytest


@pytest.mark.asyncio
async def test_list_sessions_empty(client, auth_headers):
    response = await client.get("/api/sessions", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_start_and_end_session(client, auth_headers):
    start_resp = await client.post("/api/sessions/start", headers=auth_headers)
    assert start_resp.status_code == 200
    session_id = start_resp.json()["session_id"]
    assert isinstance(session_id, int)

    end_resp = await client.post(f"/api/sessions/{session_id}/end", headers=auth_headers)
    assert end_resp.status_code == 200
    assert end_resp.json()["status"] == "ended"


@pytest.mark.asyncio
async def test_sessions_without_auth(client):
    response = await client.get("/api/sessions")
    assert response.status_code == 401
