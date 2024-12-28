import json
import pytest
from io import BytesIO
from urllib.error import HTTPError
from quipclient.quip import QuipError

def test_cache_get_request(quip_client, mock_urlopen, mock_response):
    mock_urlopen.return_value = mock_response(
        json_data={"data": "test"}
    )
    
    # First request should hit API
    result1 = quip_client._fetch_json("test", cache=True, cache_ttl=3600)
    assert mock_urlopen.call_count == 1
    
    # Second request should use cache
    result2 = quip_client._fetch_json("test", cache=True, cache_ttl=3600)
    assert mock_urlopen.call_count == 1
    assert result1 == result2

def test_cache_error_responses(quip_client, mock_urlopen):
    mock_urlopen.side_effect = HTTPError(
        "url", 403, "Forbidden", {}, 
        BytesIO(json.dumps({"error_description": "test error"}).encode())
    )
    
    # First request should hit API
    with pytest.raises(QuipError) as exc:
        quip_client._fetch_json("test", cache=True, cache_ttl=3600)
    assert mock_urlopen.call_count == 1
    
    # Second request should use cached error
    with pytest.raises(QuipError) as exc:
        quip_client._fetch_json("test", cache=True, cache_ttl=3600)
    assert mock_urlopen.call_count == 1

def test_no_cache_fetch_json(quip_client, mock_urlopen, mock_response):
    """Test that cache=False forces API calls in _fetch_json"""
    mock_urlopen.return_value = mock_response(json_data={"data": "test"})
    
    # First request hits API
    result1 = quip_client._fetch_json("test", cache=False)
    assert mock_urlopen.call_count == 1
    
    # Second request should also hit API with cache=False
    result2 = quip_client._fetch_json("test", cache=False)
    assert mock_urlopen.call_count == 2
    
def test_no_cache_cached_get(quip_client, mock_urlopen, mock_response):
    """Test that cache=False forces API calls in _cached_get"""
    mock_urlopen.return_value = mock_response(
        json_data={"ID1": {"data": "test1"}}
    )
    
    # First call should hit API
    result1 = quip_client._cached_get("threads", ["ID1"], cache=False)
    assert mock_urlopen.call_count == 1
    
    # Second call should also hit API with cache=False
    result2 = quip_client._cached_get("threads", ["ID1"], cache=False)
    assert mock_urlopen.call_count == 2
