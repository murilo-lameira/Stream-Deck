"""Barra de status do Claude Code -> Stream Deck Mi9.

Le o JSON do statusLine no stdin, envia os limites da conta ao backend local
(best effort) e imprime UMA linha em portugues. Nunca levanta excecao nem
trava a barra de status. Somente stdlib; erros apenas em stderr.
"""
import json
import sys
import urllib.request
from pathlib import Path

ENDPOINT = "http://127.0.0.1:8000/api/v1/claude/usage"
HTTP_TIMEOUT_S = 0.5
ENV_PATH = Path(__file__).resolve().parent.parent / "backend" / ".env"


def _log(msg: str) -> None:
    try:
        print(f"[claude_statusline] {msg}", file=sys.stderr)
    except Exception:
        pass


def load_token(env_path: Path) -> str | None:
    try:
        text = Path(env_path).read_text(encoding="utf-8-sig")
    except Exception:
        return None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() != "AUTH_TOKEN":
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        return value or None
    return None


def _num(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def _window(raw) -> dict | None:
    if not isinstance(raw, dict):
        return None
    pct = _num(raw.get("used_percentage"))
    resets = _num(raw.get("resets_at"))
    if pct is None or resets is None:
        return None
    return {
        "used_percentage": min(100.0, max(0.0, pct)),
        "resets_at": max(0, int(resets)),
    }


def build_body(data: dict) -> dict:
    """Monta o corpo do POST; so inclui campos presentes."""
    body: dict = {}
    limits = data.get("rate_limits")
    if isinstance(limits, dict):
        five = _window(limits.get("five_hour"))
        week = _window(limits.get("seven_day"))
        if five:
            body["five_hour"] = five
        if week:
            body["seven_day"] = week
    ctx = data.get("context_window")
    if isinstance(ctx, dict):
        pct = _num(ctx.get("used_percentage"))
        if pct is not None:
            body["context_pct"] = min(100.0, max(0.0, pct))
    model = data.get("model")
    if isinstance(model, dict):
        name = model.get("display_name")
        if isinstance(name, str) and name.strip():
            body["model"] = name.strip()[:64]
    return body


def build_line(body: dict) -> str:
    parts = []
    if body.get("model"):
        parts.append(body["model"])
    if "context_pct" in body:
        parts.append(f"contexto {round(body['context_pct'])}%")
    if "five_hour" in body:
        parts.append(f"5 h {round(body['five_hour']['used_percentage'])}%")
    if "seven_day" in body:
        parts.append(f"semana {round(body['seven_day']['used_percentage'])}%")
    return " · ".join(parts)


def post_usage(body: dict, token: str, url: str = ENDPOINT, timeout: float = HTTP_TIMEOUT_S) -> bool:
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(req, timeout=timeout) as resp:
            return resp.status in (200, 204)
    except Exception as exc:
        _log(f"POST falhou: {type(exc).__name__}")
        return False


def main() -> int:
    try:
        data = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        if not isinstance(data, dict):
            return 0
        body = build_body(data)
        if body:
            token = load_token(ENV_PATH)
            if token:
                post_usage(body, token, ENDPOINT, HTTP_TIMEOUT_S)
            else:
                _log("AUTH_TOKEN ausente")
        line = build_line(body)
        if line:
            sys.stdout.buffer.write((line + "\n").encode("utf-8"))
            sys.stdout.flush()
    except Exception as exc:
        _log(f"erro: {type(exc).__name__}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
