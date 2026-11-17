from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from routers.security_deps import require_loopback


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
