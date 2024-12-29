import os
import pytest
import asyncio
import pytest_asyncio
from quipclient.async_client import UserQuipClientAsync

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="session")
async def async_quip_client(event_loop):
    """Create async Quip client instance using API key from environment"""
    api_key = os.getenv("QUIP_API_KEY")
    base_url = os.getenv("QUIP_API_BASE_URL", "https://platform.quip.com")
    
    if not api_key:
        pytest.skip("QUIP_API_KEY environment variable not set")
    
    client = UserQuipClientAsync(
        access_token=api_key,
        base_url=base_url
    )
    await client.start()
    yield client
    await client.close()

@pytest.mark.asyncio
async def test_get_threads_v2_from_shared_folders(async_quip_client):
    """Test getting thread information from shared folders using async client"""
    # Get authenticated user to get shared folders
    user = await async_quip_client._fetch_json("users/current")
    shared_folder_ids = user.get("shared_folder_ids", [])
    
    # Skip if no shared folders
    if not shared_folder_ids:
        pytest.skip("No shared folders available")
    
    # Get first shared folder contents
    folder = await async_quip_client._fetch_json(f"folders/{shared_folder_ids[0]}")
    
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
    result = await async_quip_client._fetch_json(
        f"2/threads/",
        params={"ids": thread_ids[0]}
    )
    
    # Verify response structure
    assert len(result) > 0
    thread = next(iter(result.values()))["thread"]  # Access nested thread data
    assert "id" in thread
    assert "title" in thread
    assert "type" in thread
    assert "sharing" in thread

@pytest.mark.asyncio
async def test_get_thread_html_v2_pagination(async_quip_client):
    """Test getting complete HTML content with pagination using async client"""
    # Get thread ID from environment
    thread_id = os.getenv("QUIP_GET_HTML_PAGED")
    if not thread_id:
        pytest.skip("QUIP_GET_HTML_PAGED environment variable not set")
    
    # Get first page
    result = await async_quip_client._fetch_json(f"2/threads/{thread_id}/html")
    complete_html = result["html"]
    
    # Handle pagination
    while "response_metadata" in result and result["response_metadata"].get("next_cursor"):
        cursor = result["response_metadata"]["next_cursor"]
        result = await async_quip_client._fetch_json(
            f"2/threads/{thread_id}/html",
            params={"cursor": cursor}
        )
        complete_html += result["html"]
    
    # Verify response
    assert len(complete_html) > 0
