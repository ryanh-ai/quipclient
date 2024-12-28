import pytest
from quipclient import QuipClient

def test_get_thread(quip_client, mock_urlopen, mock_response):
    thread_data = {
        "thread": {
            "id": "test123",
            "title": "Test Thread"
        }
    }
    mock_urlopen.return_value = mock_response(json_data=thread_data)
    
    result = quip_client.get_thread("test123")
    assert result["thread"]["id"] == "test123"
    assert mock_urlopen.call_count == 1

def test_get_user(quip_client, mock_urlopen, mock_response):
    user_data = {
        "id": "test_user",
        "name": "Test User"
    }
    mock_urlopen.return_value = mock_response(json_data=user_data)
    
    result = quip_client.get_user("test_user")
    assert result["id"] == "test_user"
