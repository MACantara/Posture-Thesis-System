import pytest
from starlette.testclient import TestClient


def test_websocket_without_token(app_instance):
    client = TestClient(app_instance)
    with pytest.raises(Exception):
        with client.websocket_connect("/ws"):
            pass


def test_websocket_with_invalid_token(app_instance):
    client = TestClient(app_instance)
    with pytest.raises(Exception):
        with client.websocket_connect("/ws?token=invalidtoken"):
            pass


def test_websocket_connect_and_receive_data(app_instance, user_token):
    client = TestClient(app_instance)
    with client.websocket_connect(f"/ws?token={user_token}") as ws:
        data = ws.receive_json()
        assert "angle" in data
        assert "status" in data
        assert "accel" in data
        assert "gyro" in data
        assert "timestamp" in data


def test_websocket_recalibrate_command(app_instance, user_token):
    client = TestClient(app_instance)
    with client.websocket_connect(f"/ws?token={user_token}") as ws:
        ws.receive_json()
        ws.send_json({"type": "recalibrate"})
        response = ws.receive_json()
        assert response["type"] == "recalibrated"


def test_websocket_set_demo_state(app_instance, user_token):
    client = TestClient(app_instance)
    with client.websocket_connect(f"/ws?token={user_token}") as ws:
        ws.receive_json()
        ws.send_json({"type": "set_demo_state", "state": "good"})
        response = ws.receive_json()
        assert response["type"] == "demo_state_set"
        assert response["state"] == "good"
