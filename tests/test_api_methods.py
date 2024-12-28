import pytest
from quipclient import QuipClient
from .test_data.threads import THREAD_DATA, THREADS_DATA
from .test_data.users import USER_DATA, AUTHENTICATED_USER_DATA
from .test_data.folders import FOLDERS_DATA

def test_get_thread(quip_client, mock_urlopen, mock_response):
    mock_urlopen.return_value = mock_response(json_data=THREAD_DATA)
    
    result = quip_client.get_thread("test123")
    assert result["thread"]["id"] == "test123"
    assert mock_urlopen.call_count == 1

def test_get_user(quip_client, mock_urlopen, mock_response):
    mock_urlopen.return_value = mock_response(json_data=USER_DATA)
    
    result = quip_client.get_user("test_user")
    assert result["id"] == "test_user"

def test_get_authenticated_user(quip_client, mock_urlopen, mock_response):
    # Clear any cached errors first
    quip_client._cache.clear()
    
    mock_urlopen.return_value = mock_response(
        json_data=AUTHENTICATED_USER_DATA,
        headers={'X-RateLimit-Limit': '50'}
    )
    
    result = quip_client.get_authenticated_user()
    assert result["id"] == "auth_user"
    assert result["emails"][0] == "user@example.com"
    assert mock_urlopen.call_count == 1

def test_get_folders(quip_client, mock_urlopen, mock_response):
    mock_urlopen.return_value = mock_response(json_data=FOLDERS_DATA)
    
    result = quip_client.get_folders(["folder1", "folder2", "folder3"])
    assert len(result) == 3
    assert result["folder1"]["folder"]["title"] == "Mock Folder 1"
    assert result["folder2"]["folder"]["title"] == "Mock Folder 2" 
    assert result["folder3"]["folder"]["title"] == "Mock Folder 3"

def test_get_threads(quip_client, mock_urlopen, mock_response):
    mock_urlopen.return_value = mock_response(json_data=THREADS_DATA)
    
    result = quip_client.get_threads(["thread1", "thread2", "thread3"])
    assert len(result) == 3
    assert result["thread1"]["thread"]["title"] == "Mock Thread 1"
    assert result["thread2"]["thread"]["title"] == "Mock Thread 2"
    assert result["thread3"]["thread"]["title"] == "Template Document"
