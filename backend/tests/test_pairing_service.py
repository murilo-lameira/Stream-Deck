import json
from unittest.mock import MagicMock

import pytest

from services import pairing_service
from services.pairing_service import PairingService


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def notify():
    return MagicMock(return_value=True)


@pytest.fixture
def svc(clock, notify):
    return PairingService(notify, clock=clock, token_provider=lambda: "tok-123")


def last_code(notify):
    return notify.call_args.args[0]


def wrong_of(code):
    return "0000" if code != "0000" else "0001"


async def make_request(svc, notify, ip="1.1.1.1"):
    status, body = await svc.request(ip)
    assert status == 200
    return body["pair_id"], last_code(notify)


@pytest.mark.asyncio
async def test_code_is_4_digits_with_leading_zero(svc, notify, monkeypatch):
    monkeypatch.setattr(pairing_service.secrets, "randbelow", lambda n: 7)
    status, body = await svc.request("1.1.1.1")
    assert status == 200
    assert body["expires_in"] == 120
    assert notify.call_args.args == ("0007", "1.1.1.1")


@pytest.mark.asyncio
async def test_confirm_ok_returns_token_and_consumes(svc, notify):
    pair_id, code = await make_request(svc, notify)
    assert svc.confirm(pair_id, code, "1.1.1.1") == (200, {"auth_token": "tok-123"})
    assert svc.confirm(pair_id, code, "1.1.1.1")[0] == 410


@pytest.mark.asyncio
async def test_wrong_code_decrements_attempts(svc, notify):
    pair_id, code = await make_request(svc, notify)
    w = wrong_of(code)
    assert svc.confirm(pair_id, w, "1.1.1.1") == (401, {"attempts_left": 4})
    assert svc.confirm(pair_id, w, "1.1.1.1") == (401, {"attempts_left": 3})


@pytest.mark.asyncio
async def test_fifth_wrong_invalidates(svc, notify):
    pair_id, code = await make_request(svc, notify)
    w = wrong_of(code)
    for _ in range(4):
        assert svc.confirm(pair_id, w, "1.1.1.1")[0] == 401
    assert svc.confirm(pair_id, w, "1.1.1.1") == (401, {"attempts_left": 0})
    assert svc.confirm(pair_id, code, "1.1.1.1")[0] == 410


@pytest.mark.asyncio
async def test_expired_410(svc, notify, clock):
    pair_id, code = await make_request(svc, notify)
    clock.advance(121)
    assert svc.confirm(pair_id, code, "1.1.1.1")[0] == 410


@pytest.mark.asyncio
async def test_new_request_same_ip_replaces(svc, notify, clock):
    old_id, old_code = await make_request(svc, notify)
    clock.advance(11)
    new_id, _ = await make_request(svc, notify)
    assert new_id != old_id
    assert svc.confirm(old_id, old_code, "1.1.1.1")[0] == 410


@pytest.mark.asyncio
async def test_confirm_other_ip_410(svc, notify):
    pair_id, code = await make_request(svc, notify)
    assert svc.confirm(pair_id, code, "2.2.2.2")[0] == 410
    assert svc.confirm(pair_id, code, "1.1.1.1")[0] == 200


@pytest.mark.asyncio
async def test_cooldown_429_retry_after(svc, notify, clock):
    await make_request(svc, notify)
    clock.advance(3.5)
    status, body = await svc.request("1.1.1.1")
    assert status == 429
    assert body == {"retry_after": 7}
    clock.advance(7)
    assert (await svc.request("1.1.1.1"))[0] == 200


@pytest.mark.asyncio
async def test_max_active_429(svc, notify):
    for ip in ("1.1.1.1", "2.2.2.2", "3.3.3.3"):
        await make_request(svc, notify, ip)
    status, body = await svc.request("4.4.4.4")
    assert status == 429
    assert body["retry_after"] >= 1


@pytest.mark.asyncio
async def test_lock_after_15_wrong_even_rotating_requests(svc, notify, clock):
    for _ in range(3):
        pair_id, code = await make_request(svc, notify)
        for _ in range(4):
            assert svc.confirm(pair_id, wrong_of(code), "1.1.1.1")[0] == 401
        clock.advance(11)
    pair_id, code = await make_request(svc, notify)
    for _ in range(2):
        assert svc.confirm(pair_id, wrong_of(code), "1.1.1.1")[0] == 401
    status, body = svc.confirm(pair_id, wrong_of(code), "1.1.1.1")
    assert status == 423
    assert body["retry_after"] >= 1
    assert svc.confirm(pair_id, code, "1.1.1.1")[0] == 423
    assert (await svc.request("9.9.9.9"))[0] == 423


@pytest.mark.asyncio
async def test_lock_releases_after_900s(svc, notify, clock):
    for _ in range(3):
        pair_id, code = await make_request(svc, notify)
        for _ in range(4):
            svc.confirm(pair_id, wrong_of(code), "1.1.1.1")
        clock.advance(11)
    pair_id, code = await make_request(svc, notify)
    for _ in range(3):
        status, _ = svc.confirm(pair_id, wrong_of(code), "1.1.1.1")
    assert status == 423
    clock.advance(901)
    pair_id, code = await make_request(svc, notify)
    assert svc.confirm(pair_id, wrong_of(code), "1.1.1.1") == (401, {"attempts_left": 4})
    assert svc.confirm(pair_id, code, "1.1.1.1")[0] == 200


@pytest.mark.asyncio
async def test_notify_false_503_no_pending(svc, notify):
    notify.return_value = False
    status, body = await svc.request("1.1.1.1")
    assert status == 503
    assert body == {"detail": "Não foi possível mostrar o código no PC"}
    assert svc._pending == {}


@pytest.mark.asyncio
async def test_notify_raises_503_no_pending(svc, notify):
    notify.side_effect = RuntimeError("boom")
    status, _ = await svc.request("1.1.1.1")
    assert status == 503
    assert svc._pending == {}


@pytest.mark.asyncio
async def test_code_not_in_any_response(svc, notify, clock, monkeypatch):
    monkeypatch.setattr(pairing_service.secrets, "randbelow", lambda n: 1234)
    responses = []
    status, body = await svc.request("1.1.1.1")
    responses.append((status, body))
    responses.append(await svc.request("1.1.1.1"))
    pair_id = body["pair_id"]
    responses.append(svc.confirm(pair_id, "0000", "1.1.1.1"))
    responses.append(svc.confirm(pair_id, "1234", "2.2.2.2"))
    responses.append(svc.confirm(pair_id, "1234", "1.1.1.1"))
    for _, b in responses:
        assert "1234" not in json.dumps(b)


@pytest.mark.asyncio
async def test_max_active_429_does_not_start_cooldown(svc, notify, clock):
    for ip in ("1.1.1.1", "2.2.2.2", "3.3.3.3"):
        await make_request(svc, notify, ip)
    status, body = await svc.request("4.4.4.4")
    assert status == 429
    clock.advance(body["retry_after"])
    assert (await svc.request("4.4.4.4"))[0] == 200


@pytest.mark.asyncio
async def test_notify_503_with_previous_pending_leaves_none(svc, notify, clock):
    await make_request(svc, notify)
    clock.advance(11)
    notify.return_value = False
    assert (await svc.request("1.1.1.1"))[0] == 503
    assert svc._pending == {}
    assert (await svc.request("1.1.1.1"))[0] == 429


@pytest.mark.asyncio
async def test_lock_across_multiple_ips(svc, notify, clock):
    ids = {}
    for ip in ("1.1.1.1", "2.2.2.2"):
        ids[ip] = await make_request(svc, notify, ip)
    status = None
    for i in range(15):
        ip = "1.1.1.1" if i % 2 == 0 else "2.2.2.2"
        pair_id, code = ids[ip]
        status, _ = svc.confirm(pair_id, wrong_of(code), ip)
        if status == 401 and _["attempts_left"] == 0:
            clock.advance(11)
            ids[ip] = await make_request(svc, notify, ip)
    assert status == 423


@pytest.mark.asyncio
async def test_concurrent_requests_never_exceed_max_active(clock):
    import asyncio
    import threading

    gate = threading.Event()

    def blocking_notify(code, ip):
        gate.wait(5)
        return True

    svc = PairingService(blocking_notify, clock=clock, token_provider=lambda: "t")
    task = asyncio.gather(*[svc.request(f"10.0.0.{i}") for i in range(4)])
    await asyncio.sleep(0.1)
    gate.set()
    results = await task
    assert sorted(r[0] for r in results) == [200, 200, 200, 429]
    assert len(svc._pending) == 3


@pytest.mark.asyncio
async def test_lock_during_inflight_notify_gives_423_no_pending(clock):
    import asyncio
    import threading

    gate = threading.Event()

    def blocking_notify(code, ip):
        gate.wait(5)
        return True

    svc = PairingService(blocking_notify, clock=clock, token_provider=lambda: "t")
    task = asyncio.create_task(svc.request("1.1.1.1"))
    await asyncio.sleep(0.1)
    svc._locked_until = clock.now + 900
    gate.set()
    status, body = await task
    assert status == 423
    assert body["retry_after"] >= 1
    assert svc._pending == {}
