"""Leitura periodica dos limites da conta do Claude (mesma fonte do /usage).

Le o token de login do Claude Code em ~/.claude/.credentials.json e consulta
https://api.anthropic.com/api/oauth/usage. O token nunca e logado nem enviado
a outro host. Nao renova o token: se expirou, espera o Claude Code renovar.
API interna e sem documentacao; qualquer falha so pula a rodada.
"""
import asyncio
import json
import logging
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Optional

from services import claude_usage_service
from managers.connection_manager import manager

logger = logging.getLogger("streamdeck.claude_usage")

USAGE_URL = "https://api.anthropic.com/api/oauth/usage"
CREDENTIALS_PATH = Path.home() / ".claude" / ".credentials.json"
POLL_INTERVAL_S = 300
HTTP_TIMEOUT_S = 10


def read_access_token(path: Path = CREDENTIALS_PATH, now: Optional[float] = None) -> Optional[str]:
    """Token OAuth do Claude Code, ou None se ausente/expirado."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        oauth = data["claudeAiOauth"]
        token = oauth["accessToken"]
        expires_ms = oauth.get("expiresAt")
    except Exception:
        return None
    if not isinstance(token, str) or not token:
        return None
    now = time.time() if now is None else now
    if isinstance(expires_ms, (int, float)) and expires_ms / 1000 <= now:
        return None
    return token


def _window(raw) -> Optional[dict]:
    if not isinstance(raw, dict):
        return None
    pct = raw.get("utilization")
    resets = raw.get("resets_at")
    if isinstance(pct, bool) or not isinstance(pct, (int, float)) or not isinstance(resets, str):
        return None
    try:
        resets_at = int(datetime.fromisoformat(resets.replace("Z", "+00:00")).timestamp())
    except ValueError:
        return None
    return {"used_percentage": min(100.0, max(0.0, float(pct))), "resets_at": max(0, resets_at)}


def parse_usage(data) -> tuple[Optional[dict], Optional[dict]]:
    """Converte a resposta do endpoint em (five_hour, seven_day) no formato do store."""
    if not isinstance(data, dict):
        return None, None
    return _window(data.get("five_hour")), _window(data.get("seven_day"))


def fetch_usage(token: str, url: str = USAGE_URL, timeout: float = HTTP_TIMEOUT_S) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "anthropic-beta": "oauth-2025-04-20",
            "User-Agent": "streamdeck-usage",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


async def poll_once() -> bool:
    """Uma rodada: le, guarda e faz broadcast se preciso. True se leu algo."""
    token = await asyncio.to_thread(read_access_token)
    if not token:
        logger.info("Uso da conta: token do Claude Code ausente ou expirado; pulando.")
        return False
    try:
        data = await asyncio.to_thread(fetch_usage, token)
    except urllib.error.HTTPError as exc:
        logger.warning("Uso da conta: HTTP %s", exc.code)
        return False
    except Exception as exc:
        logger.warning("Uso da conta: falha %s", type(exc).__name__)
        return False
    five, week = parse_usage(data)
    if five is None and week is None:
        return False
    store = claude_usage_service.store
    if store.update(five_hour=five, seven_day=week):
        await manager.broadcast(store.snapshot())
    return True


async def usage_poll_loop(interval: float = POLL_INTERVAL_S) -> None:
    while True:
        try:
            await poll_once()
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.warning("Uso da conta: erro inesperado %s", type(exc).__name__)
        await asyncio.sleep(interval)
