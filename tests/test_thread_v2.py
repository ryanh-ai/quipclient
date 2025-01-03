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
    print("\nStarting test_get_thread_v2")
    mock_urlopen.return_value = mock_response(json_data=BASIC_THREAD_V2)
    
    result = quip_client.get_thread_v2("THREAD123")
    print("Got result from get_thread_v2")
    
    assert result["thread"]["id"] == "THREAD123"
    assert result["thread"]["title"] == "Test Document"
    assert result["thread"]["type"] == "DOCUMENT"
    assert "sharing" in result["thread"]
    print("Completed test_get_thread_v2")

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
    # Setup mock response
    mock_urlopen.return_value = mock_response(json_data=THREAD_FOLDERS_V2)
    
    # Call the API
    result = quip_client.get_thread_folders_v2("THREAD123", timeout=5)
    
    # Verify response structure
    assert len(result["folders"]) == 2
    assert result["folders"][0]["folder_id"] == "FOLDER1"
    assert result["folders"][0]["type"] == "SHARED"
    
    # Verify pagination metadata
    assert "response_metadata" in result
    assert "next_cursor" in result["response_metadata"]
    assert result["response_metadata"]["next_cursor"] == ""  # Should be empty after pagination

def test_get_thread_html_v2(quip_client, mock_urlopen, mock_response):
    """Test getting thread HTML with v2 API including pagination"""
    # Setup mock responses for pagination
    first_page = {
        "html": "<h1>Document Title</h1><p>First page</p>",
        "response_metadata": {"next_cursor": "page2"}
    }
    second_page = {
        "html": "<p>Second page</p>",
        "response_metadata": {"next_cursor": ""}
    }
    
    # Configure mock to return different responses for each call
    mock_urlopen.side_effect = [
        mock_response(json_data=first_page),
        mock_response(json_data=second_page)
    ]
    
    # Make the API call
    result = quip_client.get_thread_html_v2("THREAD123")
    
    # Verify the response
    assert "html" in result
    assert result["html"].startswith("<h1>Document Title</h1>")
    assert "<p>First page</p>" in result["html"]
    assert "<p>Second page</p>" in result["html"]
    assert "response_metadata" in result
    assert result["response_metadata"]["next_cursor"] == ""  # Empty after all pages
    
    # Verify correct URLs were called
    calls = mock_urlopen.call_args_list
    first_url = calls[0][0][0].get_full_url()
    second_url = calls[1][0][0].get_full_url()
    
    assert "cursor" not in first_url
    assert "cursor=page2" in second_url

def test_thread_v2_pagination_url_construction(quip_client, mock_urlopen, mock_response):
    """Test that pagination URLs are correctly constructed"""
    # Setup mock responses
    first_page = {
        "folders": [{"folder_id": "FOLDER1"}],
        "response_metadata": {"next_cursor": "page2_cursor"}
    }
    second_page = {
        "folders": [{"folder_id": "FOLDER2"}],
        "response_metadata": {"next_cursor": ""}
    }
    mock_urlopen.side_effect = [
        mock_response(json_data=first_page),
        mock_response(json_data=second_page)
    ]

    # Make API calls
    quip_client.get_thread_folders_v2("THREAD123")
    quip_client.get_thread_folders_v2("THREAD123", cursor="page2_cursor")

    # Verify URL construction
    calls = mock_urlopen.call_args_list
    first_url = calls[0][0][0].get_full_url()
    second_url = calls[1][0][0].get_full_url()
    
    assert "cursor" not in first_url
    assert "cursor=page2_cursor" in second_url

def test_thread_v2_pagination_flow(quip_client, mock_urlopen, mock_response):
    """Test complete pagination flow including response handling"""
    # Mock first page response
    first_page = {
        "folders": [
            {"folder_id": "FOLDER1", "type": "SHARED"},
            {"folder_id": "FOLDER2", "type": "PRIVATE"}
        ],
        "response_metadata": {
            "next_cursor": "page2_cursor"
        }
    }
    
    # Mock second page response
    second_page = {
        "folders": [
            {"folder_id": "FOLDER3", "type": "SHARED"},
            {"folder_id": "FOLDER4", "type": "PRIVATE"}
        ],
        "response_metadata": {
            "next_cursor": ""  # Empty cursor indicates no more pages
        }
    }
    
    # Setup mock to return different responses for each call
    mock_urlopen.side_effect = [
        mock_response(json_data=first_page),
        mock_response(json_data=second_page)
    ]
    
    # First call should get first page and include cursor in response
    result1 = quip_client.get_thread_folders_v2("THREAD123")
    assert len(result1["folders"]) == 2
    assert result1["folders"][0]["folder_id"] == "FOLDER1"
    assert result1["response_metadata"]["next_cursor"] == "page2_cursor"
    
    # Second call with cursor should get second page
    result2 = quip_client.get_thread_folders_v2(
        "THREAD123",
        cursor="page2_cursor"
    )
    assert len(result2["folders"]) == 2
    assert result2["folders"][0]["folder_id"] == "FOLDER3"
    assert result2["response_metadata"]["next_cursor"] == ""  # Empty indicates end
