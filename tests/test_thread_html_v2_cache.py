import json
import time
import zlib
import pytest
from unittest.mock import Mock

def test_get_thread_html_v2_basic_caching(quip_client, mock_urlopen, mock_response):
    """Test basic caching behavior of get_thread_html_v2"""
    # Setup mock responses for pagination
    responses = [
        {
            "html": "<h1>Page 1</h1>",
            "response_metadata": {"next_cursor": "page2"}
        },
        {
            "html": "<p>Page 2</p>",
            "response_metadata": {"next_cursor": ""}
        }
    ]
    mock_urlopen.side_effect = [mock_response(json_data=r) for r in responses]
    
    # First call should hit API
    result1 = quip_client.get_thread_html_v2("TEST123", cache=True)
    assert mock_urlopen.call_count == 2  # Two pages
    assert result1["html"] == "<h1>Page 1</h1><p>Page 2</p>"
    
    # Reset mock for second call
    mock_urlopen.reset_mock()
    
    # Second call should use cache
    result2 = quip_client.get_thread_html_v2("TEST123")
    assert mock_urlopen.call_count == 0  # No API calls
    assert result2["html"] == "<h1>Page 1</h1><p>Page 2</p>"

def test_get_thread_html_v2_cache_expiration(quip_client, mock_urlopen, mock_response):
    """Test cache expiration behavior"""
    mock_urlopen.return_value = mock_response(json_data={
        "html": "<h1>Test</h1>",
        "response_metadata": {"next_cursor": ""}
    })
    
    # First call with 1 second TTL
    result1 = quip_client.get_thread_html_v2("TEST123", cache_ttl=1)
    assert mock_urlopen.call_count == 1
    
    # Second call immediately should use cache
    mock_urlopen.reset_mock()
    result2 = quip_client.get_thread_html_v2("TEST123", cache=True)
    assert mock_urlopen.call_count == 0
    
    # Wait for cache to expire
    time.sleep(1.1)
    
    # Third call should hit API again
    result3 = quip_client.get_thread_html_v2("TEST123")
    assert mock_urlopen.call_count == 1

def test_get_thread_html_v2_compression(quip_client, mock_urlopen, mock_response):
    """Test that cached data is properly compressed/decompressed"""
    test_html = "<h1>Test</h1>" * 1000  # Create large HTML content
    mock_urlopen.return_value = mock_response(json_data={
        "html": test_html,
        "response_metadata": {"next_cursor": ""}
    })
    
    # First call to populate cache
    result1 = quip_client.get_thread_html_v2("TEST123", cache=True)
    
    # Get raw cached data
    cache_key = f"{quip_client._user_id}:https://platform.quip.com/2/threads/TEST123/html"
    cached_data = quip_client._cache.get(cache_key)
    
    # Verify data is compressed
    assert len(cached_data) < len(test_html)
    
    # Verify we can decompress and get original content
    decompressed = json.loads(zlib.decompress(cached_data).decode())
    assert decompressed["html"] == test_html

def test_get_thread_html_v2_cache_key(quip_client, mock_urlopen, mock_response):
    """Test that cache keys are properly constructed with user ID"""
    mock_urlopen.return_value = mock_response(json_data={
        "html": "<h1>Test</h1>",
        "response_metadata": {"next_cursor": ""}
    })
    
    # Call with different user IDs
    quip_client._user_id = "USER1"
    result1 = quip_client.get_thread_html_v2("TEST123", cache=True)
    
    quip_client._user_id = "USER2"
    result2 = quip_client.get_thread_html_v2("TEST123", cache=True)
    
    # Verify separate cache entries were created
    assert mock_urlopen.call_count == 2

def test_get_thread_html_v2_cache_disabled(quip_client, mock_urlopen, mock_response):
    """Test behavior when caching is disabled"""
    mock_urlopen.return_value = mock_response(json_data={
        "html": "<h1>Test</h1>",
        "response_metadata": {"next_cursor": ""}
    })
    
    # First call with cache=False
    result1 = quip_client.get_thread_html_v2("TEST123", cache=False)
    assert mock_urlopen.call_count == 1
    
    # Second call should also hit API
    result2 = quip_client.get_thread_html_v2("TEST123", cache=False)
    assert mock_urlopen.call_count == 2
