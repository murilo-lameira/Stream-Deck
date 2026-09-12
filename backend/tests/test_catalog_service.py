import os
import json
from services.catalog_service import load_catalog, save_catalog, DEFAULT_CATALOG

def test_load_catalog_returns_pages():
    catalog = load_catalog()
    assert isinstance(catalog, dict)
    assert "pages" in catalog
    assert len(catalog["pages"]) >= 3
    page_ids = [p["id"] for p in catalog["pages"]]
    assert "page_apps" in page_ids
    assert "page_media" in page_ids
    assert "page_tools" in page_ids

def test_get_deck_catalog_endpoint(test_client):
    response = test_client.get("/api/v1/deck/catalog")
    assert response.status_code == 200
    data = response.json()
    assert "pages" in data
    assert len(data["pages"]) >= 3

def test_websocket_receives_catalog_on_auth(test_client, test_token):
    with test_client.websocket_connect("/ws") as ws:
        ws.send_json({"auth_token": test_token})
        data = ws.receive_json()
        assert data.get("type") == "auth_success"
        assert "catalog" in data
        assert "pages" in data["catalog"]

def test_websocket_get_catalog_action(test_client, test_token):
    with test_client.websocket_connect("/ws") as ws:
        ws.send_json({"auth_token": test_token})
        ws.receive_json() # auth_success

        ws.send_json({"action": "get_catalog"})
        res = ws.receive_json()
        assert res.get("type") == "catalog_updated"
        assert "catalog" in res

