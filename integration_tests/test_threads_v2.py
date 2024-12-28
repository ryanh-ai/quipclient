import os
import pytest

def test_get_threads_v2_from_shared_folders(quip_client, shared_folder_ids):
    """Test getting thread information from shared folders"""
    # Skip if no shared folders
    if not shared_folder_ids:
        pytest.skip("No shared folders available")
    
    # Get first shared folder contents
    folder = quip_client.get_folder(shared_folder_ids[0])
    
    # Get thread IDs from folder children
    thread_ids = [
        child["thread_id"] 
        for child in folder.get("children", [])
        if "thread_id" in child
    ]
    
    # Skip if no threads in folder
    if not thread_ids:
        pytest.skip("No threads in first shared folder")
    
    # Test get_threads_v2 with first thread
    result = quip_client.get_threads_v2([thread_ids[0]])
    
    # Verify response structure
    assert len(result) > 0
    thread = next(iter(result.values()))["thread"]  # Access nested thread data
    assert "id" in thread
    assert "title" in thread
    assert "type" in thread
    assert "sharing" in thread

def test_get_thread_html_v2_pagination(quip_client):
    """Test getting complete HTML content with pagination"""
    # Get thread ID from environment
    thread_id = os.getenv("QUIP_GET_HTML_PAGED")
    if not thread_id:
        pytest.skip("QUIP_GET_HTML_PAGED environment variable not set")
    
    # Get complete HTML content with pagination
    result = quip_client.get_thread_html_v2(thread_id, cache=False)
    
    # Verify response structure
    assert "html" in result
    assert len(result["html"]) > 0
    assert "response_metadata" in result
    assert "next_cursor" in result["response_metadata"]
    assert result["response_metadata"]["next_cursor"] == ""  # Should be empty after all pages
