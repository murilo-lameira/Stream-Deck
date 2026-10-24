import hashlib
import pytest
from services.media_service import set_current_art, get_current_art, clear_media_art, get_image_mime_type

# Bytes de teste simulando cabeçalhos válidos de imagem
DUMMY_PNG = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4"
DUMMY_JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00"

@pytest.fixture(autouse=True)
def cleanup_art():
    clear_media_art()
    yield
    clear_media_art()

def test_set_and_get_current_art_png():
    art_hash, has_art = set_current_art(DUMMY_PNG)
    expected_hash = hashlib.md5(DUMMY_PNG).hexdigest()
    assert has_art is True
    assert art_hash == expected_hash

    data, h, mime = get_current_art()
    assert data == DUMMY_PNG
    assert h == expected_hash
    assert mime == "image/png"

def test_set_and_get_current_art_jpeg():
    art_hash, has_art = set_current_art(DUMMY_JPEG)
    expected_hash = hashlib.md5(DUMMY_JPEG).hexdigest()
    assert has_art is True
    assert art_hash == expected_hash

    data, h, mime = get_current_art()
    assert data == DUMMY_JPEG
    assert h == expected_hash
    assert mime == "image/jpeg"

def test_set_current_art_none_clears():
    set_current_art(DUMMY_PNG)
    art_hash, has_art = set_current_art(None)
    assert has_art is False
    assert art_hash is None

    data, h, mime = get_current_art()
    assert data is None
    assert h is None

def test_set_current_art_reused_cache():
    hash1, _ = set_current_art(DUMMY_PNG)
    hash2, _ = set_current_art(DUMMY_PNG)
    assert hash1 == hash2

def test_endpoint_get_media_art_not_found(test_client):
    clear_media_art()
    response = test_client.get("/api/v1/deck/media/art")
    assert response.status_code == 404
    assert "Nenhuma capa" in response.json()["detail"]

def test_endpoint_get_media_art_success_jpeg(test_client):
    art_hash, _ = set_current_art(DUMMY_JPEG)
    response = test_client.get("/api/v1/deck/media/art")
    assert response.status_code == 200
    assert response.content == DUMMY_JPEG
    assert "image/jpeg" in response.headers["content-type"]
    assert response.headers["etag"] == f'"{art_hash}"'
    assert "public" in response.headers["cache-control"]
    assert "max-age=3600" in response.headers["cache-control"]

def test_endpoint_get_media_art_with_version_query(test_client):
    art_hash, _ = set_current_art(DUMMY_PNG)
    response = test_client.get(f"/api/v1/deck/media/art?v={art_hash}")
    assert response.status_code == 200
    assert response.content == DUMMY_PNG
    assert "image/png" in response.headers["content-type"]
    assert response.headers["etag"] == f'"{art_hash}"'

def test_endpoint_if_none_match_304(test_client):
    art_hash, _ = set_current_art(DUMMY_PNG)

    # 1. Com aspas duplas padrão RFC
    response = test_client.get("/api/v1/deck/media/art", headers={"If-None-Match": f'"{art_hash}"'})
    assert response.status_code == 304
    assert response.headers["etag"] == f'"{art_hash}"'
    assert "max-age=3600" in response.headers["cache-control"]
    assert len(response.content) == 0

    # 2. Sem aspas
    response = test_client.get("/api/v1/deck/media/art", headers={"If-None-Match": art_hash})
    assert response.status_code == 304

    # 3. Validador fraco W/"..."
    response = test_client.get("/api/v1/deck/media/art", headers={"If-None-Match": f'W/"{art_hash}"'})
    assert response.status_code == 304

def test_endpoint_if_none_match_modified_200(test_client):
    art_hash, _ = set_current_art(DUMMY_PNG)
    response = test_client.get("/api/v1/deck/media/art", headers={"If-None-Match": '"outdated_hash_value"'})
    assert response.status_code == 200
    assert response.content == DUMMY_PNG
    assert response.headers["etag"] == f'"{art_hash}"'

@pytest.mark.asyncio
async def test_telemetry_broadcast_format(monkeypatch):
    import asyncio
    from unittest.mock import AsyncMock
    from services.telemetry_service import system_telemetry_loop
    from managers.connection_manager import manager

    mock_broadcast = AsyncMock()
    monkeypatch.setattr(manager, "broadcast", mock_broadcast)
    monkeypatch.setattr(manager, "active_connections", ["mock_ws"])

    mock_media = {
        "title": "Song Test",
        "artist": "Artist Test",
        "source_app": "Spotify.exe",
        "is_playing": True,
        "raw_thumbnail": DUMMY_PNG
    }

    async def mock_fetch():
        return mock_media

    monkeypatch.setattr("services.telemetry_service.fetch_media_info", mock_fetch)
    monkeypatch.setattr("services.telemetry_service.get_mic_mute_state", lambda: False)
    monkeypatch.setattr("services.telemetry_service.get_running_app_keys", AsyncMock(return_value=["spotify"]))
    monkeypatch.setattr("services.telemetry_service.get_system_metrics", AsyncMock(return_value={"cpu": 10, "ram": 20}))

    task = asyncio.create_task(system_telemetry_loop())
    await asyncio.sleep(0.05)
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

    assert mock_broadcast.called
    sent_payload = mock_broadcast.call_args[0][0]
    assert sent_payload["type"] == "system_status"
    now_playing = sent_payload["now_playing"]
    assert now_playing["title"] == "Song Test"
    assert now_playing["has_thumbnail"] is True
    expected_hash = hashlib.md5(DUMMY_PNG).hexdigest()
    assert now_playing["thumbnail_url"] == f"/api/v1/deck/media/art?v={expected_hash}"
    assert "thumbnail" not in now_playing
