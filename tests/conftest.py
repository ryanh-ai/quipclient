import json
import pytest
from unittest.mock import Mock
from io import BytesIO
from quipclient.quip import QuipClient
from urllib.error import HTTPError
import time

def pytest_configure(config):
    """Configure pytest-asyncio default fixture loop scope"""
    config.addinivalue_line(
        "asyncio_default_fixture_loop_scope",
        "function"
    )

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
def quip_client(tmp_path, mock_urlopen, mock_response):
    """Returns a QuipClient instance with a temporary cache directory and mocked auth"""
    # Setup mock response for get_authenticated_user
    mock_urlopen.return_value = mock_response(json_data={
        "id": "TEST_USER_ID",
        "name": "Test User",
        "emails": ["test@example.com"]
    })
    
    client = QuipClient(
        access_token="test_token",
        cache_dir=str(tmp_path / "cache")
    )
    
    # Reset mock for subsequent test calls
    mock_urlopen.reset_mock()
    return client

@pytest.fixture
def mock_urlopen(monkeypatch):
    """Mocks urllib's urlopen for testing HTTP requests"""
    mock = Mock()
    monkeypatch.setattr("quipclient.base.urlopen", mock)
    return mock
