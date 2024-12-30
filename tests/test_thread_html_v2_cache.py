import json
import time
import zlib
import pytest
from unittest.mock import Mock

import os
import gzip
import json
import time
from datetime import datetime

def test_get_thread_html_v2_basic_caching(quip_client, mock_urlopen, mock_response):
    """Test basic caching behavior of get_thread_html_v2"""
    # Setup mock responses for thread metadata and HTML pagination
    last_modified = int(time.time())
    thread_response = {
        "thread": {
            "id": "TEST123",
            "updated_usec": last_modified,
            "title": "Test Thread"
        }
    }
    html_responses = [
        {
            "html": "<h1>Page 1</h1>",
            "response_metadata": {
                "next_cursor": "page2"
            }
        },
        {
            "html": "<p>Page 2</p>",
            "response_metadata": {
                "next_cursor": ""
            }
        }
    ]
    # Create response objects once to reuse
    thread_mock = mock_response(json_data=thread_response)
    html_mocks = [mock_response(json_data=r) for r in html_responses]
        
    # First call responses
    mock_urlopen.side_effect = [thread_mock] + html_mocks
    
    # First call should hit API and create cache file
    result1 = quip_client.get_thread_html_v2("TEST123", cache=True)
    assert mock_urlopen.call_count == 3  # Two pages + thread metadata call
    assert result1["html"] == "<h1>Page 1</h1><p>Page 2</p>"
    
    # Verify cache file exists
    cache_path = os.path.join(quip_client._cache_dir, "html_content")
    cache_file = f"TEST123_{last_modified}.gz"
    assert os.path.exists(os.path.join(cache_path, cache_file))
    
    # Reset mock for second call
    # Reset mock and set up second call responses
    mock_urlopen.reset_mock()
    mock_urlopen.side_effect = [thread_mock]  # Only needs thread metadata for cache check
    
    # Second call should use cache
    result2 = quip_client.get_thread_html_v2("TEST123")
    assert mock_urlopen.call_count == 0  # No API calls
    assert result2["html"] == "<h1>Page 1</h1><p>Page 2</p>"

def test_get_thread_html_v2_compression(quip_client, mock_urlopen, mock_response):
    """Test that cached data is properly compressed/decompressed"""
    test_html = "<h1>Test</h1>" * 1000  # Create large HTML content
    last_modified = int(time.time())
    thread_response = {
        "thread": {
            "id": "TEST123",
            "updated_usec": last_modified,
            "title": "Test Thread"
        }
    }
    html_response = {
        "html": test_html,
        "response_metadata": {
            "next_cursor": ""
        }
    }
    mock_urlopen.side_effect = [
        mock_response(json_data=thread_response),
        mock_response(json_data=html_response)
    ]
    
    # First call to populate cache
    result1 = quip_client.get_thread_html_v2("TEST123", cache=True)
    
    # Get raw cached data
    cache_path = os.path.join(quip_client._cache_dir, "html_content")
    cache_file = os.path.join(cache_path, f"TEST123_{last_modified}.gz")
    
    # Verify file exists and is compressed
    assert os.path.exists(cache_file)
    file_size = os.path.getsize(cache_file)
    assert file_size < len(test_html)
    
    # Verify we can decompress and get original content
    with gzip.open(cache_file, 'rt') as f:
        cached_html = json.load(f)
        assert cached_html["html"] == test_html


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
