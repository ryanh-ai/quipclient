import pytest
from quipclient import QuipClient
from .test_data.users import BASIC_USER, EMAIL_USER, AUTH_USER
from .test_data.folders import PRIVATE_FOLDER, SHARED_FOLDER
from .test_data.threads import SIMPLE_THREAD, COMPLEX_THREAD

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
