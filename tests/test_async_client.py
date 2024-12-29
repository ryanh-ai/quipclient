"""Tests for async Quip client"""

import pytest
import pytest_asyncio
from aiohttp import web
from unittest.mock import Mock
from quipclient.async_client import UserQuipClientAsync

@pytest_asyncio.fixture(scope="function")
async def mock_aiohttp_app(aiohttp_server):
    """Create mock aiohttp application"""
    app = web.Application()
    
    async def mock_current_user(request):
        return web.json_response(
            {"id": "TEST_USER_ID", "name": "Test User"},
            headers={
                "X-RateLimit-Limit": "50",
                "X-RateLimit-Remaining": "49",
                "X-RateLimit-Reset": "1609459200",
                "X-Company-RateLimit-Limit": "600",
                "X-Company-RateLimit-Remaining": "599",
                "X-Company-RateLimit-Reset": "1609459200"
            }
        )
    
    app.router.add_get("/1/users/current", mock_current_user)
    server = await aiohttp_server(app)
    return server

@pytest.fixture(scope="function")
async def mock_quip_client(mock_aiohttp_app):
    """Create mock Quip client with test server"""
    server = await mock_aiohttp_app
    client = UserQuipClientAsync(
        "test_token",
        base_url=f"http://{server.host}:{server.port}"
    )
    await client.start()
    yield client
    await client.close()

@pytest.mark.asyncio
async def test_client_initialization():
    """Test basic client initialization"""
    client = UserQuipClientAsync("test_token")
    assert client.access_token == "test_token"
    assert client.base_url == "https://platform.quip.com"
    assert client._session is None

@pytest.mark.asyncio
async def test_context_manager(mock_aiohttp_app):
    """Test async context manager"""
    server = await mock_aiohttp_app
    client = UserQuipClientAsync(
        "test_token",
        base_url=f"http://{server.host}:{server.port}"
    )
    
    async with client as c:
        assert c._session is not None
        # Verify we can make a request
        user = await c._fetch_json("users/current")
        assert user["id"] == "TEST_USER_ID"
    
    assert c._session is None

@pytest.mark.asyncio
async def test_rate_limit_tracking(mock_quip_client):
    """Test rate limit header tracking"""
    await mock_quip_client._fetch_json("users/current")
    
    assert mock_quip_client._rate_limit == 50
    assert mock_quip_client._rate_limit_remaining == 49
    assert mock_quip_client._rate_limit_reset == 1609459200
    assert mock_quip_client._company_rate_limit == 600
    assert mock_quip_client._company_rate_limit_remaining == 599
    assert mock_quip_client._company_rate_limit_reset == 1609459200
