"""Pareamento por codigo de 4 digitos, em memoria. O codigo so sai via notifier; nunca e logado."""
import asyncio
import hashlib
import hmac
import logging
import math
import secrets
import time
from dataclasses import dataclass
from typing import Callable

from services import notification_service
from services.auth_service import get_auth_token

logger = logging.getLogger("streamdeck.pairing")

_GONE = {"detail": "Código expirado ou inválido"}
_NOTIFY_FAIL = {"detail": "Não foi possível mostrar o código no PC"}


def _hash(code: str) -> bytes:
    return hashlib.sha256(code.encode("utf-8")).digest()


@dataclass
class _Pending:
    ip: str
    code_hash: bytes
    expires_at: float
    attempts: int = 0


class PairingService:
    CODE_TTL_S = 120
    MAX_ATTEMPTS = 5
    REQUEST_COOLDOWN_S = 10
    MAX_ACTIVE = 3
    LOCK_MAX_WRONG = 15
    LOCK_WINDOW_S = 900
    LOCK_DURATION_S = 900

    def __init__(
        self,
        notify: Callable[[str, str], bool],
        clock: Callable[[], float] = time.monotonic,
        token_provider: Callable[[], str] = get_auth_token,
    ):
        self.notify = notify
        self._clock = clock
        self._token_provider = token_provider
        self._pending: dict[str, _Pending] = {}
        self._last_request: dict[str, float] = {}
        self._in_flight: set[str] = set()
        self._wrong_times: list[float] = []
        self._locked_until = 0.0

    @staticmethod
    def _retry(seconds: float) -> dict:
        return {"retry_after": max(1, math.ceil(seconds))}

    def _lock_remaining(self, now: float) -> float:
        if self._locked_until and now >= self._locked_until:
            self._locked_until = 0.0
            self._wrong_times.clear()
        return self._locked_until - now if self._locked_until else 0.0

    def _purge(self, now: float) -> None:
        for pid in [p for p, v in self._pending.items() if v.expires_at <= now]:
            del self._pending[pid]

    async def request(self, client_ip: str) -> tuple[int, dict]:
        status, body = await self._request(client_ip)
        logger.info("pedido de pareamento de %s: %s", client_ip, status)
        return status, body

    async def _request(self, client_ip: str) -> tuple[int, dict]:
        now = self._clock()
        remaining = self._lock_remaining(now)
        if remaining > 0:
            return 423, self._retry(remaining)

        last = self._last_request.get(client_ip)
        if last is not None and now - last < self.REQUEST_COOLDOWN_S:
            return 429, self._retry(self.REQUEST_COOLDOWN_S - (now - last))
        if client_ip in self._in_flight:
            return 429, self._retry(self.REQUEST_COOLDOWN_S)

        self._purge(now)
        other_ips = {v.ip for v in self._pending.values() if v.ip != client_ip}
        other_ips |= self._in_flight - {client_ip}
        if len(other_ips) >= self.MAX_ACTIVE:
            expiries = [v.expires_at for v in self._pending.values() if v.ip != client_ip]
            wait = (min(expiries) - now) if expiries else self.REQUEST_COOLDOWN_S
            return 429, self._retry(wait)

        self._last_request[client_ip] = now
        for pid in [p for p, v in self._pending.items() if v.ip == client_ip]:
            del self._pending[pid]

        code = f"{secrets.randbelow(10000):04d}"
        self._in_flight.add(client_ip)
        try:
            try:
                ok = await asyncio.to_thread(self.notify, code, client_ip)
            except Exception as exc:
                logger.warning("Falha no notifier de pareamento: %s", type(exc).__name__)
                ok = False
        finally:
            self._in_flight.discard(client_ip)
        if not ok:
            return 503, dict(_NOTIFY_FAIL)

        now = self._clock()
        remaining = self._lock_remaining(now)
        if remaining > 0:
            return 423, self._retry(remaining)
        pair_id = secrets.token_urlsafe(16)
        self._pending[pair_id] = _Pending(client_ip, _hash(code), now + self.CODE_TTL_S)
        return 200, {"pair_id": pair_id, "expires_in": self.CODE_TTL_S}

    def confirm(self, pair_id: str, code: str, client_ip: str) -> tuple[int, dict]:
        status, body = self._confirm(pair_id, code, client_ip)
        logger.info("confirmacao de pareamento de %s: %s", client_ip, status)
        return status, body

    def _confirm(self, pair_id: str, code: str, client_ip: str) -> tuple[int, dict]:
        now = self._clock()
        remaining = self._lock_remaining(now)
        if remaining > 0:
            return 423, self._retry(remaining)

        self._purge(now)
        pending = self._pending.get(pair_id)
        if pending is None or pending.ip != client_ip:
            return 410, dict(_GONE)

        if hmac.compare_digest(_hash(code), pending.code_hash):
            del self._pending[pair_id]
            return 200, {"auth_token": self._token_provider()}

        pending.attempts += 1
        self._wrong_times = [t for t in self._wrong_times if now - t < self.LOCK_WINDOW_S]
        self._wrong_times.append(now)
        if len(self._wrong_times) >= self.LOCK_MAX_WRONG:
            self._locked_until = now + self.LOCK_DURATION_S
            self._wrong_times.clear()
            self._pending.pop(pair_id, None)
            logger.warning("Pareamento bloqueado por excesso de tentativas erradas")
            return 423, self._retry(self.LOCK_DURATION_S)
        if pending.attempts >= self.MAX_ATTEMPTS:
            del self._pending[pair_id]
            return 401, {"attempts_left": 0}
        return 401, {"attempts_left": self.MAX_ATTEMPTS - pending.attempts}


pairing = PairingService(notification_service.show_pairing_code)
