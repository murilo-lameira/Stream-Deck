from unittest.mock import MagicMock

import pytest

from services import pairing_service
from services.pairing_service import PairingService

REQ = "/api/v1/deck/pair/request"
CONF = "/api/v1/deck/pair/confirm"


@pytest.fixture
def notify():
    return MagicMock(return_value=True)


@pytest.fixture
def svc(monkeypatch, notify):
    fresh = PairingService(notify=notify)
    monkeypatch.setattr(pairing_service, "pairing", fresh)
    return fresh


def _code(notify) -> str:
    return notify.call_args[0][0]


def test_pair_request_forbidden_without_override(test_client, svc):
    assert test_client.post(REQ).status_code == 403


def test_pair_flow_ok(test_client, lan_override, svc, notify, test_token):
    r = test_client.post(REQ)
    assert r.status_code == 200
    pair_id = r.json()["pair_id"]
    r2 = test_client.post(CONF, json={"pair_id": pair_id, "code": _code(notify)})
    assert r2.status_code == 200
    assert r2.json()["auth_token"] == test_token


def test_pair_confirm_wrong_401(test_client, lan_override, svc, notify):
    pair_id = test_client.post(REQ).json()["pair_id"]
    wrong = "0000" if _code(notify) != "0000" else "1111"
    r = test_client.post(CONF, json={"pair_id": pair_id, "code": wrong})
    assert r.status_code == 401


def test_pair_confirm_bad_code_422(test_client, lan_override, svc):
    r = test_client.post(CONF, json={"pair_id": "abc", "code": "12a4"})
    assert r.status_code == 422


def test_pair_request_503_when_notify_fails(test_client, lan_override, svc, notify):
    notify.return_value = False
    assert test_client.post(REQ).status_code == 503


def test_pair_responses_never_contain_code(test_client, lan_override, svc, notify):
    r1 = test_client.post(REQ)
    code = _code(notify)
    pair_id = r1.json()["pair_id"]
    wrong = "0000" if code != "0000" else "1111"
    r2 = test_client.post(CONF, json={"pair_id": pair_id, "code": wrong})
    r3 = test_client.post(CONF, json={"pair_id": pair_id, "code": code})
    for r in (r1, r2, r3):
        assert code not in r.text
    assert r3.status_code == 200
