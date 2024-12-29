"""Tests for async Quip client"""

import asyncio
import pytest
import pytest_asyncio
from aiohttp import web
from unittest.mock import Mock
from quipclient.async_client import UserQuipClientAsync
from quipclient.base import QuipError

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
    return await aiohttp_server(app)

@pytest_asyncio.fixture(scope="function")
async def mock_quip_client(mock_aiohttp_app):
    """Create mock Quip client with test server"""
    client = UserQuipClientAsync(
        "test_token",
        base_url=f"http://{mock_aiohttp_app.host}:{mock_aiohttp_app.port}"
    )
    await client.start()
    yield client
    await client.close()

@pytest.fixture(scope="function")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.mark.asyncio
async def test_client_initialization():
    """Test basic client initialization"""
    client = UserQuipClientAsync("test_token")
    assert client.access_token == "test_token"
    assert client.base_url == "https://platform.quip.com"
    assert client._session is None

@pytest.mark.asyncio 
async def test_fetch_json_timeout_handling(mock_aiohttp_app):
    """Test that timeouts are properly handled in _fetch_json"""
    client = UserQuipClientAsync(
        "test_token",
        base_url=f"http://{mock_aiohttp_app.host}:{mock_aiohttp_app.port}",
        request_timeout=0.1  # Very short timeout
    )
    
    async with client:
        with pytest.raises(QuipError) as exc_info:
            await client._fetch_json("slow_endpoint")
        assert exc_info.value.code == 408
        assert "Request timeout" in str(exc_info.value)

@pytest.mark.asyncio
async def test_fetch_json_task_context(mock_aiohttp_app):
    """Test that _fetch_json works properly within task context"""
    client = UserQuipClientAsync(
        "test_token",
        base_url=f"http://{mock_aiohttp_app.host}:{mock_aiohttp_app.port}"
    )
    
    async with client:
        # This should work because we're in a task context
        result = await client._fetch_json("users/current")
        assert result["id"] == "TEST_USER_ID"

@pytest.mark.asyncio
async def test_context_manager(mock_aiohttp_app):
    """Test async context manager"""
    server = mock_aiohttp_app
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

@pytest.mark.asyncio
async def test_concurrent_requests(mock_aiohttp_app):
    """Test handling multiple concurrent requests"""
    client = UserQuipClientAsync(
        "test_token",
        base_url=f"http://{mock_aiohttp_app.host}:{mock_aiohttp_app.port}",
        max_concurrent_requests=2
    )
    
    async with client:
        # Make multiple concurrent requests
        tasks = [
            client._fetch_json("users/current")
            for _ in range(3)
        ]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        for result in results:
            assert result["id"] == "TEST_USER_ID"

@pytest.mark.asyncio
async def test_error_response_handling(mock_aiohttp_app):
    """Test handling of error responses"""
    async def mock_error_endpoint(request):
        return web.Response(
            status=429,
            body='{"error_code": 429, "error_description": "Too Many Requests"}'
        )
    
    mock_aiohttp_app.app.router.add_get("/1/error", mock_error_endpoint)
    
    client = UserQuipClientAsync(
        "test_token",
        base_url=f"http://{mock_aiohttp_app.host}:{mock_aiohttp_app.port}"
    )
    
    async with client:
        with pytest.raises(QuipError) as exc_info:
            await client._fetch_json("error")
        assert exc_info.value.code == 429
        assert "Too Many Requests" in str(exc_info.value)
