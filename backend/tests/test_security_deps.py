from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from routers.security_deps import require_lan, require_loopback


def _req(host="127.0.0.1", headers=None):
    return SimpleNamespace(
        client=SimpleNamespace(host=host) if host else None,
        headers={k.lower(): v for k, v in (headers or {}).items()},
    )


@pytest.mark.parametrize("hdrs", [
    {"Host": "127.0.0.1:8000"},
    {"Host": "localhost:8000"},
    {"Host": "[::1]:8000"},
    {"Host": "127.0.0.1:8000", "Origin": "http://localhost:8000"},
    {"Host": "127.0.0.1:8000", "Sec-Fetch-Site": "same-origin"},
])
def test_allowed(hdrs):
    assert require_loopback(_req(headers=hdrs)) is None


@pytest.mark.parametrize("hdrs", [
    {"Host": "evil.example:8000"},
    {"Host": "127.0.0.1:8000", "Origin": "http://evil.example"},
    {"Host": "127.0.0.1:8000", "Sec-Fetch-Site": "cross-site"},
    {},
])
def test_rejected_headers(hdrs):
    with pytest.raises(HTTPException) as exc:
        require_loopback(_req(headers=hdrs))
    assert exc.value.status_code == 403


def test_rejected_non_loopback_client():
    with pytest.raises(HTTPException) as exc:
        require_loopback(_req(host="192.168.0.5", headers={"Host": "127.0.0.1:8000"}))
    assert exc.value.status_code == 403


@pytest.mark.parametrize("hdrs", [
    {"Host": "192.168.15.16:8000"},
    {"Host": "streamdeck.local:8000"},
    {"Host": "192.168.15.16:8000", "Origin": "http://192.168.15.16:8000"},
])
def test_lan_allowed(hdrs):
    assert require_lan(_req(host="192.168.15.20", headers=hdrs)) is None


@pytest.mark.parametrize("host,hdrs", [
    ("8.8.8.8", {"Host": "192.168.15.16:8000"}),
    ("192.168.15.20", {"Host": "evil.example:8000"}),
    ("192.168.15.20", {"Host": "192.168.15.16:8000", "Origin": "http://evil.example"}),
    ("192.168.15.20", {"Host": "192.168.15.16:8000", "Sec-Fetch-Site": "cross-site"}),
    ("testclient", {"Host": "192.168.15.16:8000"}),
])
def test_lan_rejected(host, hdrs):
    with pytest.raises(HTTPException) as exc:
        require_lan(_req(host=host, headers=hdrs))
    assert exc.value.status_code == 403
    assert exc.value.detail == "Endpoint restrito a rede local."
