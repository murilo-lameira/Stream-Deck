import pytest
from unittest.mock import AsyncMock, patch
from services.macro_service import dispatch_webhook
from fastapi import WebSocketDisconnect

def test_static_path_traversal_prevention(test_client):
    """Garante que requisições de traversal não vazem arquivos do backend."""
    # Tenta acessar o .env ou main.py via path traversal
    response = test_client.get("/../../backend/.env")
    assert response.status_code == 200
    # O conteúdo retornado DEVE ser o index.html, e NUNCA o arquivo .env
    assert "AUTH_TOKEN" not in response.text
    assert "<!doctype html>" in response.text.lower() or "<html" in response.text.lower()

def test_put_catalog_requires_auth(test_client, test_token):
    """Garante que a atualização do catálogo exige Bearer Token."""
    # Sem autenticação
    res_unauth = test_client.put("/api/v1/deck/catalog", json={"pages": []})
    assert res_unauth.status_code == 401

    # Com autenticação válida
    with patch("routers.deck_router.save_catalog", return_value=True), \
         patch("routers.deck_router.manager.broadcast", new_callable=AsyncMock):
        res_auth = test_client.put(
            "/api/v1/deck/catalog",
            headers={"Authorization": f"Bearer {test_token}"},
            json={"pages": [{"id": "test_page", "name": "Teste", "type": "grid", "items": []}]}
        )
        assert res_auth.status_code == 200
        assert res_auth.json().get("status") == "success"

def test_orchestrate_requires_auth(test_client, test_token):
    """Garante que o endpoint de orquestração de agentes exige Bearer Token."""
    # Sem autenticação
    res_unauth = test_client.post("/api/agents/orchestrate")
    assert res_unauth.status_code == 401

    # Com autenticação válida
    with patch("services.agent_service.orchestrate_agents", new_callable=AsyncMock) as mock_orch:
        mock_orch.return_value = {"status": "ok"}
        res_auth = test_client.post(
            "/api/agents/orchestrate",
            headers={"Authorization": f"Bearer {test_token}"}
        )
        assert res_auth.status_code == 200
        assert res_auth.json().get("status") == "success"

@pytest.mark.asyncio
async def test_dispatch_webhook_ssrf_protection():
    """Garante que URLs para portas restritas de loopback ou sem scheme válido são rejeitadas."""
    # Loopback no próprio host do Stream Deck (porta 8000) e portas administrativas bloqueadas
    assert await dispatch_webhook("http://localhost:8000/webhook") is False
    assert await dispatch_webhook("http://127.0.0.1:8000/admin") is False
    assert await dispatch_webhook("http://[::1]:8000/api") is False
    assert await dispatch_webhook("http://127.0.0.1:22/ssh") is False
    assert await dispatch_webhook("http://169.254.169.254/latest/meta-data/") is False

    # Esquema não HTTP
    assert await dispatch_webhook("ftp://remote.server/upload") is False
    assert await dispatch_webhook("file:///C:/Windows/win.ini") is False
    assert await dispatch_webhook("") is False

def test_websocket_rejects_unauthorized_origin(test_client):
    """Garante que origens maliciosas de navegador externo são rejeitadas."""
    with pytest.raises(WebSocketDisconnect) as exc_info:
        with test_client.websocket_connect(
            "/ws",
            headers={"Origin": "https://malicious-website.com"}
        ) as ws:
            ws.receive_json()
    assert exc_info.value.code == 1008

def test_websocket_allows_local_and_private_origins(test_client, test_token):
    """Garante que origens mDNS (streamdeck.local) e IPs privados da LAN são permitidos."""
    # Teste 1: Origem mDNS streamdeck.local
    with test_client.websocket_connect(
        "/ws",
        headers={"Origin": "http://streamdeck.local:8000"}
    ) as ws:
        ws.send_json({"auth_token": test_token})
        res = ws.receive_json()
        assert res.get("type") == "auth_success"

    # Teste 2: Origem com IP privado da LAN (ex: 192.168.15.50)
    with test_client.websocket_connect(
        "/ws",
        headers={"Origin": "http://192.168.15.50:8000"}
    ) as ws:
        ws.send_json({"auth_token": test_token})
        res = ws.receive_json()
        assert res.get("type") == "auth_success"
