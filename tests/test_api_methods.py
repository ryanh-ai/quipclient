import pytest
from unittest.mock import Mock
from quipclient import QuipClient
from .test_data.users import BASIC_USER, EMAIL_USER, AUTH_USER
from .test_data.batch_folders import BATCH_FOLDER_TEST_CASES
from .test_data.batch_threads import BATCH_THREAD_TEST_CASES
from .test_data.folders import PRIVATE_FOLDER, SHARED_FOLDER
from .test_data.threads import SIMPLE_THREAD, COMPLEX_THREAD
from .test_data.contacts import BASIC_CONTACTS, EMPTY_CONTACTS
from .test_data.teams import BASIC_TEAMS, TEAM_WITH_MEMBERS
from .test_data.messages import BASIC_MESSAGES, MESSAGES_WITH_ATTACHMENTS
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

@pytest.mark.parametrize("test_name,test_data", [
    ("basic_contacts", BASIC_CONTACTS),
    ("empty_contacts", EMPTY_CONTACTS)
])
def test_get_contacts_variations(quip_client, mock_urlopen, mock_response, test_name, test_data):
    mock_urlopen.return_value = mock_response(json_data=test_data)
    
    result = quip_client.get_contacts()
    assert len(result["contacts"]) == len(test_data["contacts"])
    if result["contacts"]:
        assert result["contacts"][0]["id"] == test_data["contacts"][0]["id"]
        assert result["contacts"][0]["name"] == test_data["contacts"][0]["name"]

@pytest.mark.parametrize("test_name,test_data", [
    ("basic_teams", BASIC_TEAMS),
    ("team_with_members", TEAM_WITH_MEMBERS)
])
def test_get_teams_variations(quip_client, mock_urlopen, mock_response, test_name, test_data):
    mock_urlopen.return_value = mock_response(json_data=test_data)
    
    result = quip_client.get_teams()
    assert len(result["teams"]) == len(test_data["teams"])
    assert result["teams"][0]["id"] == test_data["teams"][0]["id"]
    assert result["teams"][0]["name"] == test_data["teams"][0]["name"]
    if "members" in test_data["teams"][0]:
        assert len(result["teams"][0]["members"]) == len(test_data["teams"][0]["members"])

@pytest.mark.parametrize("test_name,test_data", [
    ("basic_messages", BASIC_MESSAGES),
    ("messages_with_attachments", MESSAGES_WITH_ATTACHMENTS)
])
def test_get_messages_variations(quip_client, mock_urlopen, mock_response, test_name, test_data):
    mock_urlopen.return_value = mock_response(json_data=test_data)
    
    result = quip_client.get_messages("THREAD1")
    assert len(result) == len(test_data)
    assert result[0]["id"] == test_data[0]["id"]
    assert result[0]["author_id"] == test_data[0]["author_id"]
    assert result[0]["text"] == test_data[0]["text"]
    if "files" in test_data[0]:
        assert len(result[0]["files"]) == len(test_data[0]["files"])

@pytest.mark.parametrize("test_name,test_data", BLOB_TEST_CASES)
def test_get_blob_variations(quip_client, mock_urlopen, test_name, test_data):
    mock_resp = Mock()
    mock_resp.read = lambda: test_data["content"]
    mock_urlopen.return_value = mock_resp
    
    result = quip_client.get_blob(test_data["response"]["thread_id"], test_data["response"]["hash"])
    assert result.read() == test_data["content"]
    mock_urlopen.assert_called_once()

@pytest.mark.parametrize("test_name,test_data", BATCH_FOLDER_TEST_CASES)
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
    mock_urlopen.return_value = mock_response(json_data=test_data)
    
    result = quip_client.get_threads(list(test_data.keys()))
    
    assert len(result) == len(test_data)
    for key, value in test_data.items():
        assert result[key]["thread"]["id"] == value["thread"]["id"]
        assert result[key]["thread"]["title"] == value["thread"]["title"]
        assert result[key]["thread"]["type"] == value["thread"]["type"]
