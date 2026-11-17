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
    ) -> bool:
        """Guarda o valor novo. Retorna True se deve fazer broadcast."""
        now = self._clock()
        new = {
            "five_hour": five_hour,
            "seven_day": seven_day,
            "context_pct": context_pct,
            "model": model,
        }
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
