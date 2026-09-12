import os
import sys
import pytest
from unittest.mock import AsyncMock, patch, MagicMock

# Garante que backend está no sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Configura variável de ambiente para testes
os.environ["AUTH_TOKEN"] = "test_secret_token_123"

@pytest.fixture
def test_token():
    return "test_secret_token_123"

@pytest.fixture
def mock_discovery():
    with patch("main.discovery_service.start", new_callable=AsyncMock), \
         patch("main.discovery_service.stop", new_callable=AsyncMock), \
         patch("main.system_telemetry_loop", new_callable=AsyncMock):
        yield

@pytest.fixture
def test_client(mock_discovery):
    from fastapi.testclient import TestClient
    from main import app
    with TestClient(app) as client:
        yield client

