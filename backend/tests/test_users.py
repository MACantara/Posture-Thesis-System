import pytest


@pytest.mark.asyncio
async def test_list_users_as_admin(client, admin_headers):
    response = await client.get("/api/users", headers=admin_headers)
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= 2
    assert any(u["username"] == "user" for u in users)
    assert any(u["username"] == "admin" for u in users)


@pytest.mark.asyncio
async def test_list_users_as_user_forbidden(client, auth_headers):
    response = await client.get("/api/users", headers=auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_user_by_id(client, admin_headers):
    users_resp = await client.get("/api/users", headers=admin_headers)
    user_id = users_resp.json()[0]["id"]
    response = await client.get(f"/api/users/{user_id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["id"] == user_id


@pytest.mark.asyncio
async def test_get_nonexistent_user(client, admin_headers):
    response = await client.get("/api/users/99999", headers=admin_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_user(client, admin_headers):
    users_resp = await client.get("/api/users", headers=admin_headers)
    user_id = users_resp.json()[0]["id"]
    response = await client.patch(
        f"/api/users/{user_id}",
        headers=admin_headers,
        content='{"location": "Updated City"}',
    )
    assert response.status_code == 200
    assert response.json()["location"] == "Updated City"


@pytest.mark.asyncio
async def test_users_without_auth(client):
    response = await client.get("/api/users")
    assert response.status_code == 401
