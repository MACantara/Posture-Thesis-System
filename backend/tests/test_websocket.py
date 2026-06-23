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
