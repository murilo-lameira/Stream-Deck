import asyncio
from unittest.mock import AsyncMock

import pytest

from services.claude_permission_service import PermissionBroker, summarize


def test_summarize_bash():
    assert summarize("Bash", {"command": "ls -la"}) == "ls -la"


def test_summarize_file_tools():
    for tool in ("Edit", "Write", "Read"):
        assert summarize(tool, {"file_path": "C:/x/a.py", "content": "z"}) == "C:/x/a.py"


def test_summarize_unknown_tool_json():
    assert summarize("Grep", {"q": "ação"}) == '{"q":"ação"}'


def test_summarize_truncates_300():
    out = summarize("Bash", {"command": "ação\n" * 10000})
    assert len(out) == 300
    assert "ç" in out


@pytest.mark.asyncio
async def test_submit_broadcasts_request():
    bc = AsyncMock()
    broker = PermissionBroker(bc)
    rid = await broker.submit("Bash", {"command": "ls"}, "F:/x/Stream Deck")
    assert rid
    msg = bc.await_args.args[0]
    assert msg["type"] == "claude_permission_request"
    assert msg["request_id"] == rid
    assert msg["tool_name"] == "Bash"
    assert msg["summary"] == "ls"
    assert msg["project"] == "Stream Deck"
    assert msg["expires_in"] == 120


@pytest.mark.asyncio
async def test_project_handles_backslash_and_trailing_sep():
    bc = AsyncMock()
    broker = PermissionBroker(bc)
    await broker.submit("Bash", {}, "C:" + chr(92) + "a" + chr(92) + "Proj" + chr(92))
    assert bc.await_args.args[0]["project"] == "Proj"
    await broker.submit("Bash", {}, "")
    assert bc.await_args.args[0]["project"] == ""


@pytest.mark.asyncio
async def test_resolve_allow():
    bc = AsyncMock()
    broker = PermissionBroker(bc)
    rid = await broker.submit("Bash", {"command": "ls"}, "/x/y")
    waiter = asyncio.create_task(broker.wait(rid))
    await asyncio.sleep(0)
    assert await broker.resolve(rid, "allow") is True
    assert await waiter == "allow"
    msg = bc.await_args.args[0]
    assert msg == {"type": "claude_permission_resolved", "request_id": rid, "outcome": "allow"}
    assert broker.pending_messages() == []


@pytest.mark.asyncio
async def test_resolve_before_wait_still_returns_decision():
    broker = PermissionBroker(AsyncMock())
    rid = await broker.submit("Bash", {}, "/x")
    assert await broker.resolve(rid, "deny") is True
    assert await broker.wait(rid) == "deny"


@pytest.mark.asyncio
async def test_wait_unknown_returns_none_without_broadcast():
    bc = AsyncMock()
    broker = PermissionBroker(bc)
    assert await broker.wait("nope") is None
    bc.assert_not_awaited()


@pytest.mark.asyncio
async def test_wait_timeout_expired():
    bc = AsyncMock()
    broker = PermissionBroker(bc, timeout_s=0.05)
    rid = await broker.submit("Bash", {}, "/x")
    assert await broker.wait(rid) is None
    msg = bc.await_args.args[0]
    assert msg["type"] == "claude_permission_resolved"
    assert msg["outcome"] == "expired"
    assert broker.pending_messages() == []


@pytest.mark.asyncio
async def test_resolve_twice_second_false():
    broker = PermissionBroker(AsyncMock())
    rid = await broker.submit("Bash", {}, "/x")
    assert await broker.resolve(rid, "allow") is True
    assert await broker.resolve(rid, "deny") is False
    assert await broker.resolve("unknown", "allow") is False


@pytest.mark.asyncio
async def test_full_returns_none():
    broker = PermissionBroker(AsyncMock(), max_pending=1)
    assert await broker.submit("Bash", {}, "/x") is not None
    assert await broker.submit("Bash", {}, "/x") is None


@pytest.mark.asyncio
async def test_cancel_broadcasts_and_unknown_noop():
    bc = AsyncMock()
    broker = PermissionBroker(bc)
    rid = await broker.submit("Bash", {}, "/x")
    await broker.cancel(rid)
    assert bc.await_args.args[0]["outcome"] == "cancelled"
    assert broker.pending_messages() == []
    bc.reset_mock()
    await broker.cancel("unknown")
    bc.assert_not_awaited()


@pytest.mark.asyncio
async def test_pending_messages_expires_in_decreases():
    broker = PermissionBroker(AsyncMock(), timeout_s=2.0)
    await broker.submit("Bash", {}, "/x")
    first = broker.pending_messages()[0]["expires_in"]
    await asyncio.sleep(1.1)
    second = broker.pending_messages()[0]
    assert second["type"] == "claude_permission_request"
    assert 0 <= second["expires_in"] < first
