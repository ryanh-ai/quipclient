import pytest
from quipclient import QuipClient

def test_get_thread(quip_client, mock_urlopen, mock_response):
    thread_data = {
        "thread": {
            "id": "test123",
            "title": "Test Thread"
        }
    }
    mock_urlopen.return_value = mock_response(json_data=thread_data)
    
    result = quip_client.get_thread("test123")
    assert result["thread"]["id"] == "test123"
    assert mock_urlopen.call_count == 1

def test_get_user(quip_client, mock_urlopen, mock_response):
    user_data = {
        "id": "test_user",
        "name": "Test User"
    }
    mock_urlopen.return_value = mock_response(json_data=user_data)
    
    result = quip_client.get_user("test_user")
    assert result["id"] == "test_user"

def test_get_authenticated_user(quip_client, mock_urlopen, mock_response):
    user_data = {
        "id": "auth_user",
        "name": "Auth User",
        "emails": ["test@example.com"],
        "desktop_folder_id": "folder123"
    }
    mock_urlopen.return_value = mock_response(json_data=user_data)
    
    result = quip_client.get_authenticated_user()
    assert result["id"] == "auth_user"
    assert result["emails"][0] == "test@example.com"
    assert mock_urlopen.call_count == 1

def test_get_folders(quip_client, mock_urlopen, mock_response):
    folders_data = {
        "folder1": {
            "folder": {
                "id": "folder1",
                "title": "Test Folder 1"
            },
            "member_ids": ["user1"],
            "children": []
        },
        "folder2": {
            "folder": {
                "id": "folder2", 
                "title": "Test Folder 2"
            },
            "member_ids": ["user1"],
            "children": []
        }
    }
    mock_urlopen.return_value = mock_response(json_data=folders_data)
    
    result = quip_client.get_folders(["folder1", "folder2"])
    assert len(result) == 2
    assert result["folder1"]["folder"]["title"] == "Test Folder 1"
    assert result["folder2"]["folder"]["title"] == "Test Folder 2"

def test_get_threads(quip_client, mock_urlopen, mock_response):
    threads_data = {
        "thread1": {
            "thread": {
                "id": "thread1",
                "title": "Test Thread 1"
            },
            "html": "<h1>Content 1</h1>"
        },
        "thread2": {
            "thread": {
                "id": "thread2",
                "title": "Test Thread 2"
            },
            "html": "<h1>Content 2</h1>"
        }
    }
    mock_urlopen.return_value = mock_response(json_data=threads_data)
    
    result = quip_client.get_threads(["thread1", "thread2"])
    assert len(result) == 2
    assert result["thread1"]["thread"]["title"] == "Test Thread 1"
    assert result["thread2"]["thread"]["title"] == "Test Thread 2"
