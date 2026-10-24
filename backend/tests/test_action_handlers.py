import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from schemas.deck_schemas import DeckActionPayload
from routers.deck_router import (
    ACTION_HANDLERS,
    handle_open_action,
    handle_set_volume_action,
    handle_toggle_mute_action,
    handle_toggle_mic_action,
    handle_get_volume_action,
    handle_run_macro_action,
    handle_call_webhook_action,
    handle_get_catalog_action,
    handle_ping_action,
)

def test_action_handlers_registry():
    expected_actions = {
        "open",
        "set_volume",
        "toggle_mute",
        "toggle_mic",
        "get_volume",
        "run_macro",
        "call_webhook",
        "get_catalog",
        "ping",
    }
    assert set(ACTION_HANDLERS.keys()) == expected_actions
    for action, handler in ACTION_HANDLERS.items():
        assert callable(handler)

@pytest.mark.asyncio
async def test_handle_ping_action():
    mock_ws = AsyncMock()
    cmd = DeckActionPayload(action="ping")
    await handle_ping_action(mock_ws, cmd)
    mock_ws.send_json.assert_awaited_once_with({"type": "pong"})

@pytest.mark.asyncio
async def test_handle_get_catalog_action():
    mock_ws = AsyncMock()
    cmd = DeckActionPayload(action="get_catalog")
    with patch("routers.deck_router.load_catalog", return_value={"pages": []}):
        await handle_get_catalog_action(mock_ws, cmd)
    mock_ws.send_json.assert_awaited_once_with({
        "type": "catalog_updated",
        "catalog": {"pages": []}
    })

@pytest.mark.asyncio
async def test_handle_volume_actions():
    mock_ws = AsyncMock()
    # 1. get_volume
    with patch("routers.deck_router.get_volume_state", return_value=(75, False)):
        await handle_get_volume_action(mock_ws, DeckActionPayload(action="get_volume"))
    mock_ws.send_json.assert_awaited_with({
        "type": "volume_state",
        "level": 75,
        "muted": False
    })

    # 2. set_volume
    with patch("routers.deck_router.set_volume_level", return_value=(60, False)), \
         patch("routers.deck_router.manager.broadcast", new_callable=AsyncMock) as mock_bcast:
        await handle_set_volume_action(mock_ws, DeckActionPayload(action="set_volume", level=60))
        mock_bcast.assert_awaited_with({
            "type": "volume_state",
            "level": 60,
            "muted": False
        })

    # 3. toggle_mute
    with patch("routers.deck_router.toggle_mute", return_value=(60, True)), \
         patch("routers.deck_router.manager.broadcast", new_callable=AsyncMock) as mock_bcast:
        await handle_toggle_mute_action(mock_ws, DeckActionPayload(action="toggle_mute"))
        mock_bcast.assert_awaited_with({
            "type": "volume_state",
            "level": 60,
            "muted": True
        })

    # 4. toggle_mic
    with patch("routers.deck_router.toggle_mic_mute", return_value=True):
        await handle_toggle_mic_action(mock_ws, DeckActionPayload(action="toggle_mic"))
        mock_ws.send_json.assert_awaited_with({
            "type": "mic_state",
            "mic_muted": True
        })

@pytest.mark.asyncio
async def test_handle_open_action():
    mock_ws = AsyncMock()
    # Sucesso
    with patch("routers.deck_router.launch_app_async", AsyncMock(return_value=True)), \
         patch("routers.deck_router.get_running_app_keys", AsyncMock(return_value=["spotify"])), \
         patch("routers.deck_router.manager.broadcast", new_callable=AsyncMock) as mock_bcast:
        await handle_open_action(mock_ws, DeckActionPayload(action="open", app="spotify"))
        mock_ws.send_json.assert_awaited_with({
            "type": "action_result",
            "status": "success",
            "app": "spotify",
            "message": "Aplicativo 'spotify' disparado com sucesso."
        })
        mock_bcast.assert_awaited_with({
            "type": "running_apps_update",
            "running_apps": ["spotify"]
        })

    # Sem app especificado
    mock_ws.reset_mock()
    await handle_open_action(mock_ws, DeckActionPayload(action="open"))
    mock_ws.send_json.assert_awaited_with({
        "type": "action_result",
        "status": "error",
        "message": "Identificador do aplicativo não especificado."
    })

@pytest.mark.asyncio
async def test_handle_run_macro_and_webhook():
    mock_ws = AsyncMock()
    # Macro
    with patch("routers.deck_router.execute_macro", AsyncMock(return_value={"status": "success"})):
        await handle_run_macro_action(mock_ws, DeckActionPayload(action="run_macro", macro="focus_mode"))
        mock_ws.send_json.assert_awaited_with({
            "type": "action_result",
            "status": "success",
            "macro": "focus_mode",
            "message": "Macro 'focus_mode' executada."
        })

    # Webhook
    mock_ws.reset_mock()
    with patch("routers.deck_router.dispatch_webhook", AsyncMock(return_value=True)):
        await handle_call_webhook_action(mock_ws, DeckActionPayload(action="call_webhook", url="https://example.com/hook"))
        mock_ws.send_json.assert_awaited_with({
            "type": "action_result",
            "status": "success",
            "message": "Webhook disparado: https://example.com/hook"
        })
