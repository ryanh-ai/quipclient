import pytest
from unittest.mock import Mock
from quipclient import QuipClient
from .test_data.users import BASIC_USER, EMAIL_USER, AUTH_USER
from .test_data.batch_folders import SIMPLE_FOLDERS, EMPTY_FOLDERS
from .test_data.batch_threads import SIMPLE_THREADS, EMPTY_THREADS, BATCH_THREAD_TEST_CASES
from .test_data.folders import PRIVATE_FOLDER, SHARED_FOLDER
from .test_data.threads import SIMPLE_THREAD, COMPLEX_THREAD
from .test_data.blobs import BLOB_TEST_CASES
from io import BytesIO

@pytest.mark.parametrize("test_name,test_data", [
    ("basic_user", BASIC_USER),
    ("email_user", EMAIL_USER),
    ("auth_user", AUTH_USER)
])
def test_get_user_variations(quip_client, mock_urlopen, mock_response, test_name, test_data):
    mock_urlopen.return_value = mock_response(json_data=test_data)
    
    result = quip_client.get_user(test_data["id"])
    assert result["id"] == test_data["id"]
    assert result["name"] == test_data["name"]
    if "emails" in test_data:
        assert result["emails"] == test_data["emails"]

@pytest.mark.parametrize("test_name,test_data", [
    ("private_folder", PRIVATE_FOLDER),
    ("shared_folder", SHARED_FOLDER)
])
def test_get_folder_variations(quip_client, mock_urlopen, mock_response, test_name, test_data):
    mock_urlopen.return_value = mock_response(json_data=test_data)
    
    result = quip_client.get_folder(test_data["folder"]["id"])
    assert result["folder"]["id"] == test_data["folder"]["id"]
    assert result["folder"]["title"] == test_data["folder"]["title"]
    assert result["folder"]["folder_type"] == test_data["folder"]["folder_type"]
    assert len(result["member_ids"]) == len(test_data["member_ids"])
    assert len(result["children"]) == len(test_data["children"])

@pytest.mark.parametrize("test_name,test_data", [
    ("simple_thread", SIMPLE_THREAD),
    ("complex_thread", COMPLEX_THREAD)
])
def test_get_thread_variations(quip_client, mock_urlopen, mock_response, test_name, test_data):
    mock_urlopen.return_value = mock_response(json_data=test_data)
    
    result = quip_client.get_thread(test_data["thread"]["id"])
    assert result["thread"]["id"] == test_data["thread"]["id"]
    assert result["thread"]["title"] == test_data["thread"]["title"]
    assert "html" in result
    assert len(result["user_ids"]) == len(test_data["user_ids"])
    assert len(result["shared_folder_ids"]) == len(test_data["shared_folder_ids"])


@pytest.mark.parametrize("test_name,test_data", BLOB_TEST_CASES)
def test_get_blob_variations(quip_client, mock_urlopen, test_name, test_data):
    # Setup mock response with headers and content
    mock_resp = Mock()
    mock_resp.read = lambda: test_data["content"]
    mock_resp.headers = {
        "Content-Type": test_data["content_type"],
        "Content-Length": str(len(test_data["content"]))
    }
    mock_urlopen.return_value = mock_resp
    
    # Call get_blob with thread_id and blob_id
    result = quip_client.get_blob(test_data["thread_id"], test_data["blob_id"])
    
    # Verify the response content and headers
    assert result.read() == test_data["content"]
    assert result.headers["Content-Type"] == test_data["content_type"]
    assert int(result.headers["Content-Length"]) == len(test_data["content"])
    
    # Verify the correct URL was called
    mock_urlopen.assert_called_once()
    called_url = mock_urlopen.call_args[0][0].get_full_url()
    expected_url = f"{quip_client.base_url}/1/blob/{test_data['thread_id']}/{test_data['blob_id']}"
    assert called_url == expected_url

@pytest.mark.parametrize("test_name,test_data", [
    ("simple_folders", SIMPLE_FOLDERS),
    ("empty_folders", EMPTY_FOLDERS)
])
def test_batch_folders_variations(quip_client, mock_urlopen, mock_response, test_name, test_data):
    mock_urlopen.return_value = mock_response(json_data=test_data)
    
    result = quip_client.get_folders(list(test_data.keys()))
    
    assert len(result) == len(test_data)
    for key, value in test_data.items():
        assert result[key]["folder"]["id"] == value["folder"]["id"]
        assert result[key]["folder"]["title"] == value["folder"]["title"]
        assert result[key]["folder"]["type"] == value["folder"]["type"]

@pytest.mark.parametrize("test_name,test_data", BATCH_THREAD_TEST_CASES)
def test_batch_threads_variations(quip_client, mock_urlopen, mock_response, test_name, test_data):
    """Test fetching different batch sizes of threads"""
    mock_urlopen.return_value = mock_response(json_data=test_data)
    
    # First call to test API fetch
    result1 = quip_client.get_threads(list(test_data.keys()))
    assert len(result1) == len(test_data)
    
    # Verify the response data
    for key, value in test_data.items():
        assert result1[key]["thread"]["id"] == value["thread"]["id"]
        assert result1[key]["thread"]["title"] == value["thread"]["title"]
        assert result1[key]["thread"]["type"] == value["thread"]["type"]
    
    # Second call to test caching
    result2 = quip_client.get_threads(list(test_data.keys()))
    assert result2 == result1
    
    # Verify API was only called once due to caching
    assert mock_urlopen.call_count == 1
    
    # For large batches, verify correct batch size was used
    if len(test_data) > quip_client.MAX_THREADS_PER_REQUEST:
        expected_batches = (len(test_data) + quip_client.MAX_THREADS_PER_REQUEST - 1) \
            // quip_client.MAX_THREADS_PER_REQUEST
        assert mock_urlopen.call_count == expected_batches
