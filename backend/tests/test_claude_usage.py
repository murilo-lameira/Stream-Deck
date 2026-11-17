import importlib.util
import io
import json
import socket
import sys
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from managers.connection_manager import manager
from services import claude_usage_service
from services.claude_usage_service import UsageStore

URL = "/api/v1/claude/usage"
SCRIPT = Path(__file__).resolve().parent.parent.parent / "scripts" / "claude_statusline.py"
BODY = {
    "five_hour": {"used_percentage": 42.0, "resets_at": 1900000000},
    "seven_day": {"used_percentage": 68.0, "resets_at": 1900500000},
    "context_pct": 34.0,
    "model": "Opus 5.5",
}


class Clock:
    def __init__(self, t=1000.0):
        self.t = t

    def __call__(self):
        return self.t


@pytest.fixture
def clock():
    return Clock()


@pytest.fixture
def store(monkeypatch, clock):
    s = UsageStore(clock)
    monkeypatch.setattr(claude_usage_service, "store", s)
    return s


@pytest.fixture
def broadcast(monkeypatch):
    mock = AsyncMock()
    monkeypatch.setattr(manager, "broadcast", mock)
    return mock


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_usage_forbidden_from_lan(test_client, test_token):
    assert test_client.post(URL, json=BODY, headers=_auth(test_token)).status_code == 403


def test_usage_requires_token(test_client, loopback_override):
    assert test_client.post(URL, json=BODY).status_code == 401


@pytest.mark.parametrize(
    "bad",
    [
        {"five_hour": {"used_percentage": 101, "resets_at": 1}},
        {"seven_day": {"used_percentage": -1, "resets_at": 1}},
        {"context_pct": 150},
    ],
)
def test_usage_out_of_range_422(test_client, test_token, loopback_override, store, broadcast, bad):
    assert test_client.post(URL, json=bad, headers=_auth(test_token)).status_code == 422


def test_usage_broadcasts_with_updated_at(test_client, test_token, loopback_override, store, broadcast):
    r = test_client.post(URL, json=BODY, headers=_auth(test_token))
    assert r.status_code == 204
    broadcast.assert_awaited_once()
    msg = broadcast.await_args.args[0]
    assert msg["type"] == "claude_usage"
    assert msg["updated_at"] == 1000
    assert msg["five_hour"] == BODY["five_hour"]
    assert msg["context_pct"] == 34.0 and msg["model"] == "Opus 5.5"


def test_usage_same_post_throttled(test_client, test_token, loopback_override, store, broadcast, clock):
    test_client.post(URL, json=BODY, headers=_auth(test_token))
    clock.t += 10
    test_client.post(URL, json=BODY, headers=_auth(test_token))
    assert broadcast.await_count == 1
    clock.t += 25  # 35 s desde o ultimo broadcast
    test_client.post(URL, json=BODY, headers=_auth(test_token))
    assert broadcast.await_count == 2
    assert broadcast.await_args.args[0]["updated_at"] == 1035


def test_usage_changed_post_broadcasts(test_client, test_token, loopback_override, store, broadcast, clock):
    test_client.post(URL, json=BODY, headers=_auth(test_token))
    clock.t += 1
    test_client.post(URL, json={**BODY, "context_pct": 40.0}, headers=_auth(test_token))
    assert broadcast.await_count == 2


def test_snapshot_empty_none(store):
    assert store.snapshot() is None


def test_auth_success_without_usage_sends_nothing(test_client, test_token, store, monkeypatch):
    from starlette.websockets import WebSocket

    sent = []
    original = WebSocket.send_json

    async def spy(self, data, *a, **k):
        sent.append(data.get("type") if isinstance(data, dict) else None)
        return await original(self, data, *a, **k)

    monkeypatch.setattr(WebSocket, "send_json", spy)
    with test_client.websocket_connect("/ws") as ws:
        ws.send_json({"auth_token": test_token})
        assert ws.receive_json()["type"] == "auth_success"
    assert "auth_success" in sent
    assert "claude_usage" not in sent


def test_auth_success_with_usage_sends_snapshot(test_client, test_token, store):
    store.update(five_hour=BODY["five_hour"], context_pct=12.0, model="Opus 5.5")
    with test_client.websocket_connect("/ws") as ws:
        ws.send_json({"auth_token": test_token})
        assert ws.receive_json()["type"] == "auth_success"
        msg = ws.receive_json()
        assert msg["type"] == "claude_usage"
        assert msg["seven_day"] is None
        assert msg["five_hour"] == BODY["five_hour"]


# ---- script ----

@pytest.fixture
def sl():
    spec = importlib.util.spec_from_file_location("claude_statusline", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


SAMPLE = {
    "rate_limits": {
        "five_hour": {"used_percentage": 42.3, "resets_at": 1900000000},
        "seven_day": {"used_percentage": 68.0, "resets_at": 1900500000},
    },
    "context_window": {"used_percentage": 34.4},
    "model": {"display_name": "Opus 5.5"},
}
LINE = "Opus 5.5 · contexto 34% · 5 h 42% · semana 68%"


def _closed_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def test_script_build_body(sl):
    assert sl.build_body(SAMPLE) == {
        "five_hour": {"used_percentage": 42.3, "resets_at": 1900000000},
        "seven_day": {"used_percentage": 68.0, "resets_at": 1900500000},
        "context_pct": 34.4,
        "model": "Opus 5.5",
    }


def test_script_omits_missing(sl):
    body = sl.build_body({"model": {"display_name": "Opus 5.5"}, "rate_limits": {"five_hour": {}}})
    assert body == {"model": "Opus 5.5"}
    assert sl.build_body({}) == {}
    assert sl.build_line(body) == "Opus 5.5"


def test_script_line(sl):
    assert sl.build_line(sl.build_body(SAMPLE)) == LINE


def test_script_main_prints_line_backend_down(sl, monkeypatch, capsysbinary):
    monkeypatch.setattr(sl, "ENDPOINT", f"http://127.0.0.1:{_closed_port()}/x")
    monkeypatch.setattr(sl, "load_token", lambda p: "tok")
    stdin = io.TextIOWrapper(io.BytesIO(json.dumps(SAMPLE).encode()), encoding="utf-8")
    monkeypatch.setattr(sys, "stdin", stdin)
    assert sl.main() == 0
    assert capsysbinary.readouterr().out.decode("utf-8").strip() == LINE


def test_script_post_closed_port_no_raise(sl):
    assert sl.post_usage({"model": "x"}, "tok", f"http://127.0.0.1:{_closed_port()}/x", 0.5) is False


def test_script_garbage_stdin(sl, monkeypatch, capsysbinary):
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(b"nao e json"), encoding="utf-8"))
    assert sl.main() == 0
    assert capsysbinary.readouterr().out == b""
