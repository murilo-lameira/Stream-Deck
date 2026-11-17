"""Estado em memoria dos limites da conta do Claude Code (barra de status)."""
import time
from typing import Any, Callable, Optional

BROADCAST_INTERVAL_S = 30.0


class UsageStore:
    def __init__(self, clock: Callable[[], float] = time.time):
        self._clock = clock
        self._data: Optional[dict] = None
        self._updated_at: int = 0
        self._last_broadcast: Optional[float] = None

    def update(
        self,
        five_hour: Optional[dict] = None,
        seven_day: Optional[dict] = None,
        context_pct: Optional[float] = None,
        model: Optional[str] = None,
        rtk: Optional[dict] = None,
    ) -> bool:
        """Guarda o valor novo. Retorna True se deve fazer broadcast.

        Campos None mantem o valor anterior: a barra de status (contexto e
        modelo) e o leitor da conta (janelas de 5 h e 7 dias) se completam.
        """
        now = self._clock()
        new = dict(self._data or {
            "five_hour": None,
            "seven_day": None,
            "context_pct": None,
            "model": None,
            "rtk": None,
        })
        for key, value in (
            ("five_hour", five_hour),
            ("seven_day", seven_day),
            ("context_pct", context_pct),
            ("model", model),
            ("rtk", rtk),
        ):
            if value is not None:
                new[key] = value
        changed = new != self._data
        self._data = new
        self._updated_at = int(now)
        stale = (
            self._last_broadcast is None
            or now - self._last_broadcast >= BROADCAST_INTERVAL_S
        )
        if changed or stale:
            self._last_broadcast = now
            return True
        return False

    def snapshot(self) -> Optional[dict[str, Any]]:
        if self._data is None:
            return None
        return {"type": "claude_usage", **self._data, "updated_at": self._updated_at}


store = UsageStore()
