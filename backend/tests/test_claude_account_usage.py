import asyncio
import json
from unittest.mock import AsyncMock

import pytest

from managers.connection_manager import manager
from services import claude_account_usage as acc
from services import claude_usage_service
from services.claude_usage_service import UsageStore

SAMPLE = {
    "five_hour": {"utilization": 63.0, "resets_at": "2026-11-18T01:30:00.055164+00:00"},
    "seven_day": {"utilization": 86.0, "resets_at": "2026-11-19T04:00:00+00:00"},
    "seven_day_opus": None,
}


@pytest.fixture
def store(monkeypatch):
    s = UsageStore(lambda: 1000.0)
    monkeypatch.setattr(claude_usage_service, "store", s)
    return s


@pytest.fixture
def broadcast(monkeypatch):
    mock = AsyncMock()
    monkeypatch.setattr(manager, "broadcast", mock)
    return mock


@pytest.fixture(autouse=True)
def no_real_rtk(monkeypatch):
    monkeypatch.setattr(acc, "read_rtk", lambda: None)


RTK_JSON = {
    "summary": {"total_commands": 1313, "total_saved": 6862266, "avg_savings_pct": 94.07},
    "daily": [
        {"date": "2026-11-16", "saved_tokens": 10},
        {"date": "2026-11-17", "saved_tokens": 120000, "savings_pct": 9.4},
    ],
}


def test_parse_rtk_summary_and_today():
    assert acc.parse_rtk(RTK_JSON, "2026-11-17") == {
        "savings_pct": 94.07, "saved_total": 6862266, "saved_today": 120000,
        "today_pct": 9.4, "commands": 1313,
    }


def test_parse_rtk_no_today_entry():
    r = acc.parse_rtk(RTK_JSON, "2026-12-01")
    assert r["saved_today"] == 0 and r["today_pct"] is None


@pytest.mark.parametrize("bad", [None, {}, {"summary": {"avg_savings_pct": "x", "total_saved": 1}}])
def test_parse_rtk_bad(bad):
    assert acc.parse_rtk(bad, "2026-11-17") is None


def test_read_rtk_missing_binary(monkeypatch):
    monkeypatch.undo()  # desfaz o autouse para testar a funcao real
    monkeypatch.setattr(acc, "_rtk_exe", lambda: None)
    assert acc.read_rtk() is None


def test_poll_once_rtk_only(monkeypatch, store, broadcast):
    monkeypatch.setattr(acc, "read_access_token", lambda: None)
    monkeypatch.setattr(acc, "read_rtk", lambda: {"savings_pct": 90.0, "saved_total": 5, "saved_today": 1, "commands": 2})
    assert asyncio.run(acc.poll_once()) is True
    assert store.snapshot()["rtk"]["savings_pct"] == 90.0
    broadcast.assert_awaited_once()


def test_parse_usage_converts_iso_and_pct():
    five, week = acc.parse_usage(SAMPLE)
    assert five == {"used_percentage": 63.0, "resets_at": 1794965400}
    assert week == {"used_percentage": 86.0, "resets_at": 1795060800}


@pytest.mark.parametrize("bad", [None, [], {}, {"five_hour": {"utilization": "x", "resets_at": "y"}},
                                 {"five_hour": {"utilization": 10, "resets_at": "nao-e-data"}}])
def test_parse_usage_bad_input(bad):
    assert acc.parse_usage(bad) == (None, None)


def test_parse_usage_clamps():
    five, _ = acc.parse_usage({"five_hour": {"utilization": 130, "resets_at": "2026-11-18T01:30:00Z"}})
    assert five["used_percentage"] == 100.0


def _creds(tmp_path, expires_ms):
    p = tmp_path / "c.json"
    p.write_text(json.dumps({"claudeAiOauth": {"accessToken": "tok", "expiresAt": expires_ms}}), encoding="utf-8")
    return p


def test_read_token_valid(tmp_path):
    assert acc.read_access_token(_creds(tmp_path, 2_000_000), now=1000) == "tok"


def test_read_token_expired(tmp_path):
    assert acc.read_access_token(_creds(tmp_path, 500_000), now=1000) is None


def test_read_token_missing_file(tmp_path):
    assert acc.read_access_token(tmp_path / "nao-existe.json") is None


def test_poll_once_updates_and_broadcasts(monkeypatch, store, broadcast):
    monkeypatch.setattr(acc, "read_access_token", lambda: "tok")
    monkeypatch.setattr(acc, "fetch_usage", lambda token: SAMPLE)
    assert asyncio.run(acc.poll_once()) is True
    snap = store.snapshot()
    assert snap["five_hour"]["used_percentage"] == 63.0
    broadcast.assert_awaited_once()


def test_poll_once_without_token_skips(monkeypatch, store, broadcast):
    monkeypatch.setattr(acc, "read_access_token", lambda: None)
    called = []
    monkeypatch.setattr(acc, "fetch_usage", lambda token: called.append(1))
    assert asyncio.run(acc.poll_once()) is False
    assert called == [] and store.snapshot() is None
    broadcast.assert_not_awaited()


def test_poll_once_http_error_swallowed(monkeypatch, store, broadcast):
    def boom(token):
        raise OSError("rede")
    monkeypatch.setattr(acc, "read_access_token", lambda: "tok")
    monkeypatch.setattr(acc, "fetch_usage", boom)
    assert asyncio.run(acc.poll_once()) is False
    broadcast.assert_not_awaited()


def test_store_merge_keeps_statusline_fields(store):
    store.update(context_pct=34.0, model="Opus 5.5")
    store.update(five_hour={"used_percentage": 63.0, "resets_at": 1})
    snap = store.snapshot()
    assert snap["context_pct"] == 34.0 and snap["model"] == "Opus 5.5"
    assert snap["five_hour"]["used_percentage"] == 63.0
