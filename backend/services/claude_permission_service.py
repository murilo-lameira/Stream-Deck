import asyncio
import json
import math
import re
import secrets
import logging
import time
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Dict, List, Literal, Optional

from managers.connection_manager import manager

logger = logging.getLogger("streamdeck.claude_permission")

SUMMARY_MAX = 300
Decision = Literal["allow", "deny"]


# Controles bidi (U+202A-202E, U+2066-2069) e C0 exceto LF e TAB: trocados por U+FFFD.
_UNSAFE_CHARS = re.compile(
    "[" + chr(0x202A) + "-" + chr(0x202E) + chr(0x2066) + "-" + chr(0x2069)
    + chr(0x00) + "-" + chr(0x08) + chr(0x0B) + "-" + chr(0x1F) + "]"
)
REPLACEMENT_CHAR = chr(0xFFFD)
ELLIPSIS = chr(0x2026)


def summarize_full(tool_name: str, tool_input: dict) -> tuple[str, bool, int]:
    """Devolve (resumo exibivel, truncado, tamanho do resumo completo sanitizado)."""
    tool_input = tool_input or {}
    if tool_name == "Bash":
        text = str(tool_input.get("command", ""))
    elif tool_name in ("Edit", "Write", "Read"):
        text = str(tool_input.get("file_path", ""))
    else:
        text = json.dumps(tool_input, ensure_ascii=False, separators=(",", ":"))
    text = _UNSAFE_CHARS.sub(REPLACEMENT_CHAR, text)
    length = len(text)
    if length > SUMMARY_MAX:
        return text[: SUMMARY_MAX - 1] + ELLIPSIS, True, length
    return text, False, length


def summarize(tool_name: str, tool_input: dict) -> str:
    """Resume a chamada de ferramenta para exibir no celular (max 300 chars)."""
    return summarize_full(tool_name, tool_input)[0]


def _project_name(cwd: str) -> str:
    parts = [p for p in (cwd or "").replace("\\", "/").split("/") if p]
    return parts[-1] if parts else ""


@dataclass
class _Pending:
    tool_name: str
    summary: str
    project: str
    deadline: float
    truncated: bool = False
    summary_length: int = 0
    future: asyncio.Future = field(default_factory=lambda: asyncio.get_running_loop().create_future())


class PermissionBroker:
    def __init__(
        self,
        broadcast: Callable[[dict], Awaitable[None]],
        timeout_s: float = 120.0,
        max_pending: int = 10,
    ):
        self._broadcast = broadcast
        self._timeout_s = timeout_s
        self._max_pending = max_pending
        self._pending: Dict[str, _Pending] = {}

    def _request_message(self, request_id: str, p: _Pending) -> dict:
        remaining = max(0.0, p.deadline - time.monotonic())
        return {
            "type": "claude_permission_request",
            "request_id": request_id,
            "tool_name": p.tool_name,
            "summary": p.summary,
            "truncated": p.truncated,
            "summary_length": p.summary_length,
            "project": p.project,
            "expires_in": math.ceil(remaining),
        }

    async def _resolved(self, request_id: str, outcome: str) -> None:
        await self._broadcast(
            {"type": "claude_permission_resolved", "request_id": request_id, "outcome": outcome}
        )

    def _purge(self) -> List[str]:
        """Remove entradas decididas ou vencidas; devolve ids vencidos sem decisao."""
        now = time.monotonic()
        expired: List[str] = []
        for rid, p in list(self._pending.items()):
            if p.future.done():
                del self._pending[rid]
            elif p.deadline <= now:
                p.future.set_result(None)
                del self._pending[rid]
                expired.append(rid)
        return expired

    async def submit(self, tool_name: str, tool_input: dict, cwd: str) -> Optional[str]:
        for rid in self._purge():
            await self._resolved(rid, "expired")
        if len(self._pending) >= self._max_pending:
            return None
        request_id = secrets.token_urlsafe(16)
        summary, truncated, summary_length = summarize_full(tool_name, tool_input)
        pending = _Pending(
            tool_name=tool_name,
            summary=summary,
            project=_project_name(cwd),
            deadline=time.monotonic() + self._timeout_s,
            truncated=truncated,
            summary_length=summary_length,
        )
        self._pending[request_id] = pending
        await self._broadcast(self._request_message(request_id, pending))
        return request_id

    async def wait(self, request_id: str) -> Optional[Decision]:
        pending = self._pending.get(request_id)
        if pending is None:
            return None
        remaining = max(0.0, pending.deadline - time.monotonic())
        try:
            return await asyncio.wait_for(pending.future, timeout=remaining)
        except asyncio.TimeoutError:
            await self._resolved(request_id, "expired")
            return None
        except asyncio.CancelledError:
            # wait_for cancela o future interno; um future com resultado ja foi decidido.
            if not pending.future.done() or pending.future.cancelled():
                await self._resolved(request_id, "cancelled")
            raise
        finally:
            self._pending.pop(request_id, None)

    async def resolve(self, request_id: str, decision: Decision) -> bool:
        pending = self._pending.get(request_id)
        if pending is None or pending.future.done():
            return False
        pending.future.set_result(decision)
        await self._resolved(request_id, decision)
        return True

    async def cancel(self, request_id: str) -> None:
        pending = self._pending.pop(request_id, None)
        if pending is None:
            return
        if pending.future.done():
            return
        pending.future.set_result(None)
        await self._resolved(request_id, "cancelled")

    def pending_messages(self) -> List[dict]:
        self._purge()
        return [
            self._request_message(rid, p)
            for rid, p in self._pending.items()
            if not p.future.done()
        ]


broker = PermissionBroker(manager.broadcast)
