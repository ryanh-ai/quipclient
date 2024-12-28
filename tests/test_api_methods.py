import pytest
from quipclient import QuipClient
from .test_data.threads import THREAD_TEST_CASES
from .test_data.users import USER_TEST_CASES
from .test_data.folders import FOLDER_TEST_CASES

@pytest.mark.parametrize("test_name,test_data", USER_TEST_CASES)
def test_get_user_variations(quip_client, mock_urlopen, mock_response, test_name, test_data):
    mock_urlopen.return_value = mock_response(json_data=test_data)
    
    result = quip_client.get_user(test_data["id"])
    assert result["id"] == test_data["id"]
    assert result["name"] == test_data["name"]
    if "emails" in test_data:
        assert result["emails"] == test_data["emails"]

@pytest.mark.parametrize("test_name,test_data", FOLDER_TEST_CASES)
def test_get_folder_variations(quip_client, mock_urlopen, mock_response, test_name, test_data):
    mock_urlopen.return_value = mock_response(json_data=test_data)
    
    result = quip_client.get_folder(test_data["folder"]["id"])
    assert result["folder"]["id"] == test_data["folder"]["id"]
    assert result["folder"]["title"] == test_data["folder"]["title"]
    assert result["folder"]["folder_type"] == test_data["folder"]["folder_type"]
    assert len(result["member_ids"]) == len(test_data["member_ids"])
    assert len(result["children"]) == len(test_data["children"])

@pytest.mark.parametrize("test_name,test_data", THREAD_TEST_CASES)
def test_get_thread_variations(quip_client, mock_urlopen, mock_response, test_name, test_data):
    mock_urlopen.return_value = mock_response(json_data=test_data)
    
    result = quip_client.get_thread(test_data["thread"]["id"])
    assert result["thread"]["id"] == test_data["thread"]["id"]
    assert result["thread"]["title"] == test_data["thread"]["title"]
    assert "html" in result
    assert len(result["user_ids"]) == len(test_data["user_ids"])
    assert len(result["shared_folder_ids"]) == len(test_data["shared_folder_ids"])
