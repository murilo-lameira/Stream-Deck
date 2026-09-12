import pytest
from starlette.websockets import WebSocketDisconnect

def test_websocket_auth_success(test_client, test_token):
    with test_client.websocket_connect("/ws") as ws:
        # Envia handshake com token válido
        ws.send_json({"auth_token": test_token})
        data = ws.receive_json()
        assert data.get("type") == "auth_success"
        assert "available_apps" in data
        assert "volume" in data

def test_websocket_auth_invalid_token(test_client):
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with test_client.websocket_connect("/ws") as ws:
            ws.send_json({"auth_token": "token_errado_invalido"})
            ws.receive_json()
    assert exc_info.value.code == 1008

def test_websocket_auth_malformed_payload(test_client):
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with test_client.websocket_connect("/ws") as ws:
            ws.send_json({"campo_aleatorio": 123})
            ws.receive_json()
    assert exc_info.value.code == 1008

def test_websocket_ping_pong(test_client, test_token):
    with test_client.websocket_connect("/ws") as ws:
        ws.send_json({"auth_token": test_token})
        auth_res = ws.receive_json()
        assert auth_res.get("type") == "auth_success"

        # Envia heartbeat ping
        ws.send_json({"action": "ping"})
        pong = ws.receive_json()
        assert pong.get("type") == "pong"

