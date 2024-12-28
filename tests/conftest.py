import json
import pytest
from unittest.mock import Mock, BytesIO
from quipclient.quip import QuipClient
from urllib.error import HTTPError
import time

@pytest.fixture
def mock_response():
    """Returns a configurable mock HTTP response"""
    def _mock_response(status=200, json_data=None, headers=None):
        mock_resp = Mock()
        mock_resp.code = status
        mock_resp.headers = headers or {}
        mock_resp.read.return_value = json.dumps(json_data or {}).encode()
        return mock_resp
    return _mock_response

@pytest.fixture
def quip_client(tmp_path):
    """Returns a QuipClient instance with a temporary cache directory"""
    return QuipClient(
        access_token="test_token",
        cache_dir=str(tmp_path / "cache")
    )

@pytest.fixture
def mock_urlopen(monkeypatch):
    """Mocks urllib's urlopen for testing HTTP requests"""
    mock = Mock()
    monkeypatch.setattr("quipclient.quip.urlopen", mock)
    return mock
