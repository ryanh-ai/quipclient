import pytest
from quipclient import QuipClient
from .test_data.threads_v2 import (
    BASIC_THREAD_V2,
    THREAD_FOLDERS_V2,
    THREAD_HTML_V2,
    MULTIPLE_THREADS_V2
)

def test_get_thread_v2(quip_client, mock_urlopen, mock_response):
    """Test getting a single thread with v2 API"""
    mock_urlopen.return_value = mock_response(json_data=BASIC_THREAD_V2)
    
    result = quip_client.get_thread_v2("THREAD123")
    
    assert result["thread"]["id"] == "THREAD123"
    assert result["thread"]["title"] == "Test Document"
    assert result["thread"]["type"] == "DOCUMENT"
    assert "sharing" in result["thread"]

def test_get_threads_v2(quip_client, mock_urlopen, mock_response):
    """Test getting multiple threads with v2 API"""
    mock_urlopen.return_value = mock_response(json_data=MULTIPLE_THREADS_V2)
    
    result = quip_client.get_threads_v2(["THREAD1", "THREAD2"])
    
    assert len(result) == 2
    assert result["THREAD1"]["id"] == "THREAD123"
    assert result["THREAD2"]["id"] == "THREAD2"
    assert all("sharing" in thread for thread in result.values())

def test_get_thread_folders_v2(quip_client, mock_urlopen, mock_response):
    """Test getting thread folders with v2 API"""
    mock_urlopen.return_value = mock_response(json_data=THREAD_FOLDERS_V2)
    
    result = quip_client.get_thread_folders_v2("THREAD123")
    
    assert len(result["folders"]) == 2
    assert result["folders"][0]["folder_id"] == "FOLDER1"
    assert result["folders"][0]["type"] == "SHARED"
    assert "response_metadata" in result
    assert "next_cursor" in result["response_metadata"]

def test_get_thread_html_v2(quip_client, mock_urlopen, mock_response):
    """Test getting thread HTML with v2 API"""
    mock_urlopen.return_value = mock_response(json_data=THREAD_HTML_V2)
    
    result = quip_client.get_thread_html_v2("THREAD123")
    
    assert "html" in result
    assert result["html"].startswith("<h1>Document Title</h1>")
    assert "response_metadata" in result
    assert "next_cursor" in result["response_metadata"]

def test_thread_v2_pagination(quip_client, mock_urlopen, mock_response):
    """Test pagination parameters for v2 API methods"""
    mock_urlopen.return_value = mock_response(json_data=THREAD_FOLDERS_V2)
    
    result = quip_client.get_thread_folders_v2(
        "THREAD123",
        cursor="page2",
        limit=10
    )
    
    # Verify the URL contains pagination parameters
    called_url = mock_urlopen.call_args[0][0].get_full_url()
    assert "cursor=page2" in called_url
    assert "limit=10" in called_url
