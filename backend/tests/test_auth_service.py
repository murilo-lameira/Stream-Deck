import os
import pytest
from unittest.mock import patch
from services.auth_service import get_auth_token, rotate_token, generate_pairing_url, is_valid_token, DEFAULT_INSECURE_TOKEN

def test_get_auth_token_returns_existing(test_token):
    token = get_auth_token()
    assert token == test_token

def test_get_auth_token_rotates_insecure(monkeypatch, tmp_path):
    monkeypatch.setenv("AUTH_TOKEN", DEFAULT_INSECURE_TOKEN)
    fake_env = tmp_path / ".env"
    fake_env.write_text("AUTH_TOKEN=mi9_deck_secret_2026\n", encoding="utf-8")
    monkeypatch.setattr("services.auth_service._get_dotenv_path", lambda: str(fake_env))

    new_token = get_auth_token()
    assert new_token != DEFAULT_INSECURE_TOKEN
    assert len(new_token) > 20
    assert os.environ["AUTH_TOKEN"] == new_token
    assert f"AUTH_TOKEN={new_token}" in fake_env.read_text(encoding="utf-8")

def test_rotate_token(monkeypatch, tmp_path):
    fake_env = tmp_path / ".env"
    fake_env.write_text("HOST=0.0.0.0\n", encoding="utf-8")
    monkeypatch.setattr("services.auth_service._get_dotenv_path", lambda: str(fake_env))

    token1 = rotate_token()
    token2 = rotate_token()
    assert token1 != token2
    assert os.environ["AUTH_TOKEN"] == token2
    assert f"AUTH_TOKEN={token2}" in fake_env.read_text(encoding="utf-8")

def test_generate_pairing_url(test_token):
    url = generate_pairing_url("192.168.1.50", 8000)
    assert url == f"http://192.168.1.50:8000?token={test_token}"

def test_endpoint_get_pairing_info(test_client, test_token, loopback_override):
    response = test_client.get("/api/v1/deck/pairing")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["auth_token"] == test_token
    assert f"?token={test_token}" in data["pairing_url"]

def test_legacy_token_rejected():
    assert is_valid_token(DEFAULT_INSECURE_TOKEN) is False

def test_pairing_forbidden_from_lan(test_client):
    response = test_client.get("/api/v1/deck/pairing")
    assert response.status_code == 403

def test_pairing_uses_lan_ip(test_client, loopback_override):
    with patch("routers.deck_router.get_local_ip", return_value="192.168.0.9"):
        response = test_client.get("/api/v1/deck/pairing")
    assert response.status_code == 200
    assert response.json()["pairing_url"].startswith("http://192.168.0.9:")

def test_endpoint_rotate_pairing_token_unauthorized(test_client):
    response = test_client.post("/api/v1/deck/pairing/rotate")
    assert response.status_code == 401

def test_endpoint_rotate_pairing_token_authorized(test_client, test_token, monkeypatch, tmp_path):
    fake_env = tmp_path / ".env"
    fake_env.write_text(f"AUTH_TOKEN={test_token}\n", encoding="utf-8")
    monkeypatch.setattr("services.auth_service._get_dotenv_path", lambda: str(fake_env))

    headers = {"Authorization": f"Bearer {test_token}"}
    response = test_client.post("/api/v1/deck/pairing/rotate", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    new_token = data["auth_token"]
    assert new_token != test_token
    assert f"?token={new_token}" in data["pairing_url"]

    # Reverte para manter os testes limpos
    monkeypatch.setenv("AUTH_TOKEN", test_token)


def test_get_auth_token_reads_dotenv_when_env_missing(tmp_path, monkeypatch):
    """Regressao: sem AUTH_TOKEN no ambiente (import antes do load_dotenv), o token do .env
    deve ser reaproveitado, sem gerar outro nem reescrever o arquivo."""
    from services import auth_service
    env = tmp_path / ".env"
    env.write_text("HOST=0.0.0.0\nAUTH_TOKEN=token-existente-123\n", encoding="utf-8")
    before = env.read_bytes()
    monkeypatch.setattr(auth_service, "_get_dotenv_path", lambda: str(env))
    monkeypatch.delenv("AUTH_TOKEN", raising=False)
    assert auth_service.get_auth_token() == "token-existente-123"
    assert env.read_bytes() == before


def test_get_auth_token_generates_when_dotenv_has_none(tmp_path, monkeypatch):
    from services import auth_service
    env = tmp_path / ".env"
    env.write_text("HOST=0.0.0.0\n", encoding="utf-8")
    monkeypatch.setattr(auth_service, "_get_dotenv_path", lambda: str(env))
    monkeypatch.delenv("AUTH_TOKEN", raising=False)
    tok = auth_service.get_auth_token()
    assert tok and tok != auth_service.DEFAULT_INSECURE_TOKEN
    assert f"AUTH_TOKEN={tok}" in env.read_text(encoding="utf-8")
