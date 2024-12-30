import os
import time
import pytest

def test_thread_html_v2_caching_integration(quip_client, shared_folder_ids):
    """Integration test for thread HTML caching"""
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
        
    test_thread_id = thread_ids[0]
    
    # First call - should hit API and create cache
    start_time = time.time()
    result1 = quip_client.get_thread_html_v2(test_thread_id, cache=True)
    first_call_time = time.time() - start_time
    
    # Verify response structure
    assert "html" in result1
    assert len(result1["html"]) > 0
    assert "response_metadata" in result1
    
    # Verify cache file exists
    thread_data = quip_client.get_thread_v2(test_thread_id)
    thread_usec = thread_data["thread"]["updated_usec"]
    cache_path = os.path.join(quip_client._cache_dir, "html_content")
    cache_file = os.path.join(cache_path, f"{test_thread_id}_{thread_usec}.gz")
    assert os.path.exists(cache_file)
    
    # Second call - should use cache and be faster
    start_time = time.time()
    result2 = quip_client.get_thread_html_v2(test_thread_id, cache=True)
    second_call_time = time.time() - start_time
    
    # Verify cached response matches original
    assert result2["html"] == result1["html"]
    
    # Verify second call was faster (cached)
    assert second_call_time < first_call_time
