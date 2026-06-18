import pytest


@pytest.mark.asyncio
async def test_login_valid_user(client):
    response = await client.post("/api/auth/login", json={
        "username": "user",
        "password": "pass123",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["role"] == "user"
    assert data["username"] == "user"
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_valid_admin(client):
    response = await client.post("/api/auth/login", json={
        "username": "admin",
        "password": "admin123",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["role"] == "admin"
    assert data["username"] == "admin"


@pytest.mark.asyncio
async def test_login_invalid_password(client):
    response = await client.post("/api/auth/login", json={
        "username": "user",
        "password": "wrongpassword",
    })
    assert response.status_code == 401
    assert "Invalid" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    response = await client.post("/api/auth/login", json={
        "username": "nobody",
        "password": "pass123",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_with_valid_token(client, auth_headers):
    response = await client.get("/api/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "user"
    assert data["role"] == "user"


@pytest.mark.asyncio
async def test_get_me_without_token(client):
    response = await client.get("/api/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_with_invalid_token(client):
    response = await client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalidtoken123"},
    )
    assert response.status_code == 401
