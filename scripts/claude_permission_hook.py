"""Hook PermissionRequest do Claude Code -> Stream Deck Mi9.

Encaminha o pedido ao backend local e imprime a decisao. Qualquer falha
resulta em NENHUMA decisao: saida vazia e codigo 0 (o Claude Code mostra o
prompt normal no PC). Somente stdlib; logs apenas em stderr.
"""
import json
import sys
import urllib.request
from pathlib import Path

ENDPOINT = "http://127.0.0.1:8000/api/v1/claude/permission"
HTTP_TIMEOUT_S = 125.0
DENY_MESSAGE = "Negado pelo Stream Deck (celular)."
ENV_PATH = Path(__file__).resolve().parent.parent / "backend" / ".env"


def _log(msg: str) -> None:
    print(f"[claude_permission_hook] {msg}", file=sys.stderr)


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


def build_output(behavior: str) -> dict | None:
    if behavior == "allow":
        decision = {"behavior": "allow"}
    elif behavior == "deny":
        decision = {"behavior": "deny", "message": DENY_MESSAGE}
    else:
        return None
    return {
        "hookSpecificOutput": {
            "hookEventName": "PermissionRequest",
            "decision": decision,
        }
    }


def request_decision(
    payload: dict, token: str, url: str = ENDPOINT, timeout: float = HTTP_TIMEOUT_S
) -> str | None:
    try:
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            url,
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status != 200:
                return None
            data = json.loads(resp.read().decode("utf-8"))
        behavior = data.get("behavior") if isinstance(data, dict) else None
        return behavior if behavior in ("allow", "deny") else None
    except Exception as exc:
        _log(f"sem decisao: {type(exc).__name__}")
        return None


def main() -> int:
    try:
        payload = json.loads(sys.stdin.buffer.read().decode("utf-8"))
        if not isinstance(payload, dict):
            return 0
        token = load_token(ENV_PATH)
        if not token:
            _log("AUTH_TOKEN ausente")
            return 0
        behavior = request_decision(payload, token, ENDPOINT, HTTP_TIMEOUT_S)
        output = build_output(behavior) if behavior else None
        if output is not None:
            sys.stdout.write(json.dumps(output) + "\n")
            sys.stdout.flush()
    except Exception as exc:
        _log(f"erro: {type(exc).__name__}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
