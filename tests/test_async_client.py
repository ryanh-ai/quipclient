"""Tests for async Quip client"""

import pytest
import aiohttp
from unittest.mock import Mock
from quipclient.async_client import UserQuipClientAsync

@pytest.mark.asyncio
async def test_client_initialization():
    """Test basic client initialization"""
    client = UserQuipClientAsync("test_token")
    assert client.access_token == "test_token"
    assert client.base_url == "https://platform.quip.com"
    assert client._session is None
    
@pytest.mark.asyncio
async def test_context_manager():
    """Test async context manager"""
    async with UserQuipClientAsync("test_token") as client:
        assert client._session is not None
    assert client._session is None

@pytest.mark.asyncio
async def test_rate_limit_tracking(aiohttp_client):
    """Test rate limit header tracking"""
    headers = {
        "X-RateLimit-Limit": "50",
        "X-RateLimit-Remaining": "49",
        "X-RateLimit-Reset": "1609459200",
        "X-Company-RateLimit-Limit": "600",
        "X-Company-RateLimit-Remaining": "599",
        "X-Company-RateLimit-Reset": "1609459200"
    }
    
    async def mock_handler(request):
        return aiohttp.web.json_response(
            {"id": "TEST_USER_ID", "name": "Test User"},
            headers=headers
        )
    
    app = aiohttp.web.Application()
    app.router.add_get("/1/users/current", mock_handler)
    client = await aiohttp_client(app)
    
    quip = UserQuipClientAsync("test_token", base_url="")
    quip._session = client
    
    await quip._fetch_json("users/current")
    
    assert quip._rate_limit == 50
    assert quip._rate_limit_remaining == 49
    assert quip._rate_limit_reset == 1609459200
    assert quip._company_rate_limit == 600
    assert quip._company_rate_limit_remaining == 599
    assert quip._company_rate_limit_reset == 1609459200
