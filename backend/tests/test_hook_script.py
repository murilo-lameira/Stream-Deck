import importlib.util
import io
import json
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent.parent / "scripts" / "claude_permission_hook.py"


def _load():
    spec = importlib.util.spec_from_file_location("claude_permission_hook", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def hook():
    return _load()


def _stdin(text: str):
    return io.TextIOWrapper(io.BytesIO(text.encode("utf-8")), encoding="utf-8")


def test_build_output_allow(hook):
    assert hook.build_output("allow") == {
        "hookSpecificOutput": {
            "hookEventName": "PermissionRequest",
            "decision": {"behavior": "allow"},
        }
    }


def test_build_output_deny_has_message(hook):
    out = hook.build_output("deny")
    decision = out["hookSpecificOutput"]["decision"]
    assert decision["behavior"] == "deny"
    assert decision["message"] == hook.DENY_MESSAGE


def test_build_output_invalid_none(hook):
    assert hook.build_output("maybe") is None
    assert hook.build_output("") is None


def test_load_token(hook, tmp_path):
    env = tmp_path / ".env"
    env.write_text("# comentario\nOUTRA=1\nAUTH_TOKEN=\"abc=123\"\n", encoding="utf-8")
    assert hook.load_token(env) == "abc=123"


def test_load_token_missing_none(hook, tmp_path):
    assert hook.load_token(tmp_path / "nao_existe.env") is None
    env = tmp_path / ".env"
    env.write_text("OUTRA=1\n", encoding="utf-8")
    assert hook.load_token(env) is None


def test_main_server_down_prints_nothing(hook, monkeypatch, capsys):
    monkeypatch.setattr(hook, "ENDPOINT", "http://127.0.0.1:1/api/v1/claude/permission")
    monkeypatch.setattr(hook, "load_token", lambda p: "tok")
    monkeypatch.setattr(sys, "stdin", _stdin('{"tool_name":"Bash","x":"ação não"}'))
    assert hook.main() == 0
    assert capsys.readouterr().out == ""


def test_main_allow_prints_json(hook, monkeypatch, capsys):
    monkeypatch.setattr(hook, "load_token", lambda p: "tok")
    monkeypatch.setattr(hook, "request_decision", lambda *a, **k: "allow")
    monkeypatch.setattr(sys, "stdin", _stdin('{"tool_name":"Bash"}'))
    assert hook.main() == 0
    out = capsys.readouterr().out
    assert out.endswith("\n")
    assert '"behavior": "allow"' in out


def test_main_invalid_stdin_prints_nothing(hook, monkeypatch, capsys):
    monkeypatch.setattr(hook, "load_token", lambda p: "tok")
    monkeypatch.setattr(sys, "stdin", _stdin("nao e json"))
    assert hook.main() == 0
    assert capsys.readouterr().out == ""


@pytest.fixture
def stub():
    state = {"status": 200, "body": b'{"behavior":"allow"}'}

    class H(BaseHTTPRequestHandler):
        def do_POST(self):
            n = int(self.headers.get("Content-Length", 0))
            self.rfile.read(n)
            self.send_response(state["status"])
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(state["body"])))
            self.end_headers()
            self.wfile.write(state["body"])

        def log_message(self, *a):
            pass

    srv = HTTPServer(("127.0.0.1", 0), H)
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    state["url"] = f"http://127.0.0.1:{srv.server_address[1]}/api/v1/claude/permission"
    yield state
    srv.shutdown()
    srv.server_close()


def test_request_decision_ignores_env_proxy(hook, stub, monkeypatch):
    for k in ("HTTP_PROXY", "http_proxy"):
        monkeypatch.setenv(k, "http://127.0.0.1:9")
    for k in ("NO_PROXY", "no_proxy"):
        monkeypatch.delenv(k, raising=False)
    assert hook.request_decision({"a": 1}, "tok", stub["url"], 5) == "allow"


def test_request_decision_204_none(hook, stub):
    stub["status"], stub["body"] = 204, b""
    assert hook.request_decision({}, "tok", stub["url"], 5) is None


def test_request_decision_unknown_behavior_none(hook, stub):
    stub["body"] = b'{"behavior":"maybe"}'
    assert hook.request_decision({}, "tok", stub["url"], 5) is None


def test_request_decision_invalid_json_none(hook, stub):
    stub["body"] = b"nao e json"
    assert hook.request_decision({}, "tok", stub["url"], 5) is None


def test_main_deny_via_stub(hook, stub, monkeypatch, capsys):
    stub["body"] = b'{"behavior":"deny"}'
    monkeypatch.setattr(hook, "ENDPOINT", stub["url"])
    monkeypatch.setattr(hook, "load_token", lambda p: "tok")
    monkeypatch.setattr(sys, "stdin", _stdin('{"tool_name":"Bash"}'))
    assert hook.main() == 0
    out = json.loads(capsys.readouterr().out)
    assert out == hook.build_output("deny")
    assert out["hookSpecificOutput"]["decision"]["message"] == hook.DENY_MESSAGE
