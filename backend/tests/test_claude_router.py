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


class _StubRequest:
    def __init__(self, results):
        self._results = list(results)
        self.calls = 0

    async def is_disconnected(self):
        self.calls += 1
        if self._results:
            return self._results.pop(0)
        return False


def _outcomes(broadcast):
    return [
        c.args[0]["outcome"]
        for c in broadcast.call_args_list
        if c.args[0]["type"] == "claude_permission_resolved"
    ]


@pytest.mark.asyncio
async def test_watch_disconnect_returns_after_true(monkeypatch):
    from routers import claude_router

    real_sleep = asyncio.sleep

    async def fast_sleep(_):
        await real_sleep(0)

    monkeypatch.setattr(claude_router.asyncio, "sleep", fast_sleep)
    stub = _StubRequest([False, True])
    await asyncio.wait_for(claude_router._watch_disconnect(stub), timeout=1)
    assert stub.calls == 2


@pytest.mark.asyncio
async def test_handler_disconnect_cancels_and_returns_204(monkeypatch, fake_ws):
    from fastapi import Response
    from routers import claude_router
    from schemas.deck_schemas import ClaudePermissionHookInput

    broadcast = AsyncMock()
    b = PermissionBroker(broadcast, timeout_s=30)
    monkeypatch.setattr(claude_permission_service, "broker", b)
    result = await asyncio.wait_for(
        claude_router.claude_permission(
            ClaudePermissionHookInput(tool_name="Bash"), _StubRequest([True])
        ),
        timeout=2,
    )
    assert isinstance(result, Response)
    assert result.status_code == 204
    assert _outcomes(broadcast) == ["cancelled"]
    assert b._pending == {}


@pytest.mark.asyncio
async def test_handler_task_cancelled_broadcasts_cancelled(monkeypatch, fake_ws):
    from routers import claude_router
    from schemas.deck_schemas import ClaudePermissionHookInput

    broadcast = AsyncMock()
    b = PermissionBroker(broadcast, timeout_s=30)
    monkeypatch.setattr(claude_permission_service, "broker", b)
    task = asyncio.create_task(
        claude_router.claude_permission(
            ClaudePermissionHookInput(tool_name="Bash"), _StubRequest([])
        )
    )
    for _ in range(200):
        if b._pending:
            break
        await asyncio.sleep(0.005)
    assert b._pending
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert _outcomes(broadcast) == ["cancelled"]
    assert b._pending == {}
