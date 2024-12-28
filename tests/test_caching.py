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
