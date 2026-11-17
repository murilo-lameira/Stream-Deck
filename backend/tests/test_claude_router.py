import asyncio
from unittest.mock import AsyncMock

import httpx
import pytest

from managers.connection_manager import manager
from services import claude_permission_service
from services.claude_permission_service import PermissionBroker

URL = "/api/v1/claude/permission"


@pytest.fixture
def fake_ws():
    ws = AsyncMock()
    manager.active_connections.append(ws)
    yield ws
    if ws in manager.active_connections:
        manager.active_connections.remove(ws)


@pytest.fixture
def short_broker(monkeypatch):
    b = PermissionBroker(AsyncMock(), timeout_s=0.2)
    monkeypatch.setattr(claude_permission_service, "broker", b)
    return b


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_hook_forbidden_from_lan(test_client, test_token):
    r = test_client.post(URL, json={"tool_name": "Bash"}, headers=_auth(test_token))
    assert r.status_code == 403


def test_hook_requires_token(test_client, loopback_override):
    r = test_client.post(URL, json={"tool_name": "Bash"})
    assert r.status_code == 401


def test_hook_no_clients_204(test_client, test_token, loopback_override, short_broker):
    saved = list(manager.active_connections)
    manager.active_connections.clear()
    try:
        r = test_client.post(URL, json={"tool_name": "Bash"}, headers=_auth(test_token))
    finally:
        manager.active_connections.extend(saved)
    assert r.status_code == 204
    assert r.content == b""


def test_hook_minimal_body(test_client, test_token, loopback_override, short_broker, fake_ws):
    r = test_client.post(URL, json={"tool_name": "mcp__srv__tool"}, headers=_auth(test_token))
    assert r.status_code != 422


def test_hook_timeout_204(test_client, test_token, loopback_override, short_broker, fake_ws):
    r = test_client.post(
        URL, json={"tool_name": "Bash", "tool_input": {"command": "ls"}}, headers=_auth(test_token)
    )
    assert r.status_code == 204
    assert r.content == b""


def test_hook_full_204(test_client, test_token, loopback_override, monkeypatch, fake_ws):
    b = PermissionBroker(AsyncMock(), timeout_s=5, max_pending=0)
    monkeypatch.setattr(claude_permission_service, "broker", b)
    r = test_client.post(URL, json={"tool_name": "Bash"}, headers=_auth(test_token))
    assert r.status_code == 204


async def _flow(decision, token):
    from main import app

    b = claude_permission_service.broker

    async def decide():
        for _ in range(200):
            msgs = b.pending_messages()
            if msgs:
                await b.resolve(msgs[0]["request_id"], decision)
                return
            await asyncio.sleep(0.005)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        task = asyncio.create_task(decide())
        r = await client.post(
            URL,
            json={"tool_name": "Bash", "tool_input": {"command": "ls"}, "cwd": "C:/p"},
            headers=_auth(token),
        )
        await task
    return r


@pytest.mark.asyncio
async def test_hook_allow_flow(test_token, loopback_override, monkeypatch, fake_ws):
    monkeypatch.setattr(claude_permission_service, "broker", PermissionBroker(AsyncMock(), timeout_s=5))
    r = await _flow("allow", test_token)
    assert r.status_code == 200
    assert r.json() == {"behavior": "allow"}


@pytest.mark.asyncio
async def test_hook_deny_flow(test_token, loopback_override, monkeypatch, fake_ws):
    monkeypatch.setattr(claude_permission_service, "broker", PermissionBroker(AsyncMock(), timeout_s=5))
    r = await _flow("deny", test_token)
    assert r.status_code == 200
    assert r.json() == {"behavior": "deny"}
