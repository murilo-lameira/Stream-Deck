import importlib.util
import io
import sys
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
