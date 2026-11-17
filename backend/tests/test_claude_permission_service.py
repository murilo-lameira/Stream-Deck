import asyncio
from unittest.mock import AsyncMock

import pytest

from services.claude_permission_service import PermissionBroker, describe, summarize


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


@pytest.mark.asyncio
async def test_request_id_is_urlsafe_token():
    broker = PermissionBroker(AsyncMock())
    rid = await broker.submit("Bash", {}, "/x")
    assert len(rid) == 22
    assert all(c.isalnum() or c in "-_" for c in rid)


@pytest.mark.asyncio
async def test_wait_cancelled_broadcasts_cancelled_and_removes():
    bc = AsyncMock()
    broker = PermissionBroker(bc)
    rid = await broker.submit("Bash", {}, "/x")
    waiter = asyncio.create_task(broker.wait(rid))
    await asyncio.sleep(0)
    waiter.cancel()
    with pytest.raises(asyncio.CancelledError):
        await waiter
    msg = bc.await_args.args[0]
    assert msg == {"type": "claude_permission_resolved", "request_id": rid, "outcome": "cancelled"}
    assert broker.pending_messages() == []
    bc.reset_mock()
    await broker.cancel(rid)
    bc.assert_not_awaited()


@pytest.mark.asyncio
async def test_cancel_while_waiting_returns_none_single_broadcast():
    bc = AsyncMock()
    broker = PermissionBroker(bc)
    rid = await broker.submit("Bash", {}, "/x")
    waiter = asyncio.create_task(broker.wait(rid))
    await asyncio.sleep(0)
    bc.reset_mock()
    await broker.cancel(rid)
    assert await waiter is None
    assert bc.await_count == 1
    assert bc.await_args.args[0]["outcome"] == "cancelled"


@pytest.mark.asyncio
async def test_resolved_unawaited_does_not_occupy_slot():
    broker = PermissionBroker(AsyncMock(), max_pending=1)
    rid = await broker.submit("Bash", {}, "/x")
    assert await broker.resolve(rid, "allow") is True
    assert await broker.submit("Bash", {}, "/x") not in (None, rid)


@pytest.mark.asyncio
async def test_expired_unawaited_is_purged_with_broadcast():
    bc = AsyncMock()
    broker = PermissionBroker(bc, timeout_s=0.05, max_pending=1)
    rid = await broker.submit("Bash", {}, "/x")
    await asyncio.sleep(0.1)
    new = await broker.submit("Bash", {}, "/x")
    assert new is not None
    outcomes = [c.args[0] for c in bc.await_args_list if c.args[0]["type"] == "claude_permission_resolved"]
    assert outcomes == [{"type": "claude_permission_resolved", "request_id": rid, "outcome": "expired"}]


def test_summarize_truncated_ends_with_ellipsis():
    out = summarize("Bash", {"command": "x" * 1000})
    assert len(out) == 300
    assert out.endswith(chr(0x2026))
    assert out[:299] == "x" * 299


def test_summarize_exactly_300_not_truncated():
    assert summarize("Bash", {"command": "a" * 300}) == "a" * 300


def test_summarize_strips_bidi_and_c0_controls():
    bad = [0x202E, 0x2066, 0x2069, 0x00, 0x07, 0x1B]
    cmd = "ls" + "".join(chr(c) for c in bad) + "ok" + chr(10) + chr(9) + "end"
    out = summarize("Bash", {"command": cmd})
    for c in bad:
        assert chr(c) not in out
    assert out == "ls" + chr(0xFFFD) * len(bad) + "ok" + chr(10) + chr(9) + "end"


@pytest.mark.asyncio
async def test_request_message_truncated_fields():
    bc = AsyncMock()
    broker = PermissionBroker(bc)
    await broker.submit("Bash", {"command": "x" * 1000}, "F:/p")
    msg = bc.await_args.args[0]
    assert msg["truncated"] is True
    assert msg["summary_length"] == 1000
    assert len(msg["summary"]) == 300


@pytest.mark.asyncio
async def test_request_message_short_not_truncated():
    bc = AsyncMock()
    broker = PermissionBroker(bc)
    await broker.submit("Bash", {"command": "ls"}, "F:/p")
    msg = bc.await_args.args[0]
    assert msg["truncated"] is False
    assert msg["summary_length"] == 2


def test_summarize_powershell_not_json():
    assert summarize("PowerShell", {"command": "Get-ChildItem C:/x"}) == "Get-ChildItem C:/x"


def test_summarize_search_and_web_tools():
    assert summarize("Glob", {"pattern": "**/*.py"}) == "**/*.py"
    assert summarize("Grep", {"pattern": "foo"}) == "foo"
    assert summarize("WebFetch", {"url": "https://a.com/x"}) == "https://a.com/x"
    assert summarize("WebSearch", {"query": "fastapi"}) == "fastapi"


def test_describe_uses_input_description():
    assert describe("Bash", {"command": "ls", "description": "Listar arquivos"}) == "Listar arquivos"


def test_describe_fallback_edit_only_filename():
    assert describe("Edit", {"file_path": r"C:\Users\x\proj\main.py"}) == "Editar o arquivo main.py"


def test_describe_fallbacks_by_tool():
    assert describe("PowerShell", {}) == "Rodar um comando no PowerShell"
    assert describe("WebFetch", {"url": "https://example.com/a?b=1"}) == "Abrir a página example.com"
    assert describe("mcp__srv__do_it", {}) == "Usar a ferramenta do_it"
    assert describe("Foo", {}) == "Usar a ferramenta Foo"


def test_describe_truncates_160():
    out = describe("Bash", {"description": "a" * 500})
    assert len(out) == 160
    assert out.endswith(chr(0x2026))


def test_describe_sanitizes_bidi():
    out = describe("Bash", {"description": "ok" + chr(0x202E) + "evil"})
    assert chr(0x202E) not in out
    assert chr(0xFFFD) in out


@pytest.mark.asyncio
async def test_request_message_has_description():
    bc = AsyncMock()
    broker = PermissionBroker(bc)
    await broker.submit("PowerShell", {"command": "Get-Date"}, "F:/p")
    msg = bc.await_args.args[0]
    assert msg["description"] == "Rodar um comando no PowerShell"
    assert msg["summary"] == "Get-Date"
