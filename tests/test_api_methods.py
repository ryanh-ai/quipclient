import pytest
from quipclient import QuipClient

def test_get_thread(quip_client, mock_urlopen, mock_response):
    thread_data = {
        "thread": {
            "author_id": "ABC123xyz",
            "thread_class": "document",
            "owning_company_id": "XYZ789abc",
            "id": "DEF456uvw",
            "created_usec": 1735232430682856,
            "updated_usec": 1735232468086554,
            "title": "Mock Document",
            "link": "https://example.com/DEF456uvw",
            "document_id": "GHI789rst",
            "type": "document",
            "is_template": False,
            "is_deleted": False
        }
    }
    mock_urlopen.return_value = mock_response(json_data=thread_data)
    
    result = quip_client.get_thread("test123")
    assert result["thread"]["id"] == "test123"
    assert mock_urlopen.call_count == 1

def test_get_user(quip_client, mock_urlopen, mock_response):
    user_data = {
        "name": "Mock User",
        "id": "JKL012mno",
        "is_robot": False,
        "affinity": 0.0
    }
    mock_urlopen.return_value = mock_response(json_data=user_data)
    
    result = quip_client.get_user("test_user")
    assert result["id"] == "test_user"

def test_get_authenticated_user(quip_client, mock_urlopen, mock_response):
    # Clear any cached errors first
    quip_client._cache.clear()
    
    user_data = {
        "name": "Mock Auth User",
        "emails": ["user@example.com"],
        "id": "MNO345pqr",
        "is_robot": False,
        "affinity": 0.0,
        "desktop_folder_id": "PQR678stu",
        "archive_folder_id": "STU901vwx", 
        "starred_folder_id": "VWX234yza",
        "private_folder_id": "YZA567bcd",
        "trash_folder_id": "BCD890efg",
        "shared_folder_ids": ["EFG123hij", "HIJ456klm"],
        "group_folder_ids": [],
        "subdomain": "",
        "url": "https://example.com"
    }
    mock_urlopen.return_value = mock_response(
        json_data=user_data,
        headers={'X-RateLimit-Limit': '50'}
    )
    
    result = quip_client.get_authenticated_user()
    assert result["id"] == "auth_user"
    assert result["emails"][0] == "test@example.com"
    assert mock_urlopen.call_count == 1

def test_get_folders(quip_client, mock_urlopen, mock_response):
    folders_data = {
        "KLM789nop": {
            "folder": {
                "creator_id": "NOP012qrs",
                "folder_type": "private",
                "inherit_mode": "reset",
                "id": "KLM789nop",
                "created_usec": 1510251981120743,
                "updated_usec": 1732837192184612,
                "link": "https://example.com/KLM789nop",
                "title": "Mock Folder 1"
            },
            "member_ids": ["NOP012qrs"],
            "children": [
                {"thread_id": "QRS345tuv"},
                {"folder_id": "TUV678wxy"}
            ]
        },
        "WXY901zab": {
            "folder": {
                "creator_id": "NOP012qrs",
                "folder_type": "shared",
                "inherit_mode": "inherit",
                "id": "WXY901zab", 
                "created_usec": 1510251981120743,
                "updated_usec": 1732837192184612,
                "link": "https://example.com/WXY901zab",
                "title": "Mock Folder 2"
            },
            "member_ids": ["NOP012qrs"],
            "children": [
                {"thread_id": "CDE234fgh"},
                {"folder_id": "FGH567ijk"}
            ]
        }
    }
    mock_urlopen.return_value = mock_response(json_data=folders_data)
    
    result = quip_client.get_folders(["folder1", "folder2"])
    assert len(result) == 2
    assert result["folder1"]["folder"]["title"] == "Test Folder 1"
    assert result["folder2"]["folder"]["title"] == "Test Folder 2"

def test_get_threads(quip_client, mock_urlopen, mock_response):
    threads_data = {
        "IJK890lmn": {
            "thread": {
                "author_id": "LMN123opq",
                "thread_class": "document",
                "owning_company_id": "OPQ456rst",
                "id": "IJK890lmn",
                "created_usec": 1735232430682856,
                "updated_usec": 1735232468086554,
                "title": "Mock Thread 1",
                "link": "https://example.com/IJK890lmn",
                "document_id": "RST789uvw",
                "type": "document",
                "is_template": False
            },
            "html": "<h1>Mock Content 1</h1>",
            "user_ids": ["LMN123opq"],
            "shared_folder_ids": [],
            "access_levels": {"LMN123opq": {"access_level": "OWN"}}
        },
        "UVW012xyz": {
            "thread": {
                "author_id": "LMN123opq", 
                "thread_class": "document",
                "owning_company_id": "OPQ456rst",
                "id": "UVW012xyz",
                "created_usec": 1735232430682856,
                "updated_usec": 1735232468086554,
                "title": "Mock Thread 2",
                "link": "https://example.com/UVW012xyz",
                "document_id": "XYZ345abc",
                "type": "document",
                "is_template": False
            },
            "html": "<h1>Mock Content 2</h1>",
            "user_ids": ["LMN123opq"],
            "shared_folder_ids": [],
            "access_levels": {"LMN123opq": {"access_level": "OWN"}}
        }
    }
    mock_urlopen.return_value = mock_response(json_data=threads_data)
    
    result = quip_client.get_threads(["thread1", "thread2"])
    assert len(result) == 2
    assert result["thread1"]["thread"]["title"] == "Test Thread 1"
    assert result["thread2"]["thread"]["title"] == "Test Thread 2"
