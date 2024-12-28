import time
import pytest
from quipclient.quip import QuipClient

def test_rate_limit_tracking(quip_client, mock_urlopen, mock_response):
    current_time = time.time()
    headers = {
        'X-RateLimit-Limit': '50',
        'X-RateLimit-Remaining': '49',
        'X-RateLimit-Reset': str(current_time + 60),
        'X-Company-RateLimit-Limit': '600',
        'X-Company-RateLimit-Remaining': '599',
        'X-Company-RateLimit-Reset': str(current_time + 60)
    }
    mock_urlopen.return_value = mock_response(
        json_data={"success": True},
        headers=headers
    )
    
    result = quip_client._fetch_json("test")
    
    assert quip_client._rate_limit == 50
    assert quip_client._rate_limit_remaining == 49
    assert quip_client._company_rate_limit == 600
    assert quip_client._company_rate_limit_remaining == 599
