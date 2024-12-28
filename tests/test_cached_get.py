import pytest
from unittest.mock import Mock, call
import time

def test_cached_get_single_item(quip_client, mock_urlopen, mock_response):
    """Test fetching a single item with caching"""
    mock_urlopen.return_value = mock_response(json_data={"ID1": {"data": "test1"}})
    
    # First call should hit API
    result1 = quip_client._cached_get("threads", ["ID1"])
    assert mock_urlopen.call_count == 1
    assert result1 == {"ID1": {"data": "test1"}}
    
    # Second call should use cache
    result2 = quip_client._cached_get("threads", ["ID1"])
    assert mock_urlopen.call_count == 1
    assert result2 == {"ID1": {"data": "test1"}}

def test_cached_get_batch_size(quip_client, mock_urlopen, mock_response):
    """Test that items are fetched in correct batch sizes"""
    # Create 20 IDs
    ids = [f"ID{i}" for i in range(20)]
    
    # Setup mock to return different responses for each batch
    responses = [
        {"ID0": {"data": "batch1"}, "ID1": {"data": "batch1"}},
        {"ID2": {"data": "batch2"}, "ID3": {"data": "batch2"}},
        # ... etc for all batches
    ]
    mock_urlopen.side_effect = [mock_response(json_data=r) for r in responses]
    
    result = quip_client._cached_get("threads", ids, batch_size=2)
    
    # Should have made 10 API calls (20 items / 2 per batch)
    assert mock_urlopen.call_count == 10

def test_cached_get_mixed_cache(quip_client, mock_urlopen, mock_response):
    """Test behavior when some items are cached and others aren't"""
    # First call to cache item1
    mock_urlopen.return_value = mock_response(json_data={
        "item1": {"data": "test1"}
    })
    quip_client._cached_get("threads", ["item1"])
    mock_urlopen.reset_mock()
    
    # Second call with mix of cached and uncached
    mock_urlopen.return_value = mock_response(json_data={
        "item2": {"data": "test2"}
    })
    result = quip_client._cached_get("threads", ["item1", "item2"])
    
    # Should only fetch item2
    assert mock_urlopen.call_count == 1
    assert result == {
        "item1": {"data": "test1"},
        "item2": {"data": "test2"}
    }
