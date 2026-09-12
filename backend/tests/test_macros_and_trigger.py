import pytest
from unittest.mock import AsyncMock, patch, MagicMock

def test_get_macros_endpoint(test_client):
    response = test_client.get("/api/v1/deck/macros")
    assert response.status_code == 200
    data = response.json()
    assert "study_mode" in data
    assert "gaming_mode" in data

def test_trigger_endpoint_unauthorized(test_client):
    # Sem cabeçalho Authorization
    response = test_client.post("/api/trigger", json={"action": "set_volume", "level": 30})
    assert response.status_code == 401

    # Com token incorreto
    response = test_client.post(
        "/api/trigger",
        headers={"Authorization": "Bearer token_falso"},
        json={"action": "set_volume", "level": 30}
    )
    assert response.status_code == 401

def test_trigger_endpoint_authorized(test_client, test_token):
    mock_volume = MagicMock()
    mock_volume.GetMute.return_value = 0
    mock_speakers = MagicMock()
    mock_speakers.EndpointVolume = mock_volume

    with patch("pycaw.pycaw.AudioUtilities.GetSpeakers", return_value=mock_speakers):
        response = test_client.post(
            "/api/trigger",
            headers={"Authorization": f"Bearer {test_token}"},
            json={"action": "set_volume", "level": 40}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "success"
        assert data.get("level") == 40

def test_trigger_run_macro(test_client, test_token):
    with patch("apps_config.launch_app_async", new_callable=AsyncMock) as mock_launch, \
         patch("audio_service.set_volume_level", return_value=(30, False)), \
         patch("audio_service.set_mic_mute_state", return_value=True):
        mock_launch.return_value = True

        response = test_client.post(
            "/api/trigger",
            headers={"Authorization": f"Bearer {test_token}"},
            json={"action": "run_macro", "macro": "study_mode"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") == "success"
        assert data.get("macro") == "study_mode"
        assert len(data.get("results", [])) == 4

def test_websocket_run_macro(test_client, test_token):
    with patch("apps_config.launch_app_async", new_callable=AsyncMock) as mock_launch, \
         patch("audio_service.set_volume_level", return_value=(30, False)), \
         patch("audio_service.set_mic_mute_state", return_value=True):
        mock_launch.return_value = True

        with test_client.websocket_connect("/ws") as ws:
            ws.send_json({"auth_token": test_token})
            ws.receive_json() # auth_success

            ws.send_json({"action": "run_macro", "macro": "study_mode"})
            # Coleta mensagens até receber o action_result da macro (pode haver broadcasts de volume intermediários)
            messages = []
            for _ in range(5):
                msg = ws.receive_json()
                messages.append(msg)
                if msg.get("type") == "action_result":
                    break

            action_res = next((m for m in messages if m.get("type") == "action_result"), None)
            assert action_res is not None
            assert action_res.get("status") == "success"
            assert action_res.get("macro") == "study_mode"
