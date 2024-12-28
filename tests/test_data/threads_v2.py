"""Test data for Thread API v2 responses"""

# Basic thread response
BASIC_THREAD_V2 = {
    "thread": {
        "author_id": "USER123",
        "created_usec": 1609459200000000,
        "id": "THREAD123",
        "is_template": False,
        "link": "https://test.quip.com/abc123",
        "owning_company_id": "COMPANY1",
        "secret_path": "abc123",
        "title": "Test Document",
        "type": "DOCUMENT",
        "updated_usec": 1609545600000000,
        "sharing": {
            "company_id": "COMPANY1",
            "company_mode": "EDIT"
        }
    }
}

# Thread with folders response
THREAD_FOLDERS_V2 = {
    "folders": [
        {
            "folder_id": "FOLDER1",
            "type": "SHARED"
        },
        {
            "folder_id": "FOLDER2", 
            "type": "PRIVATE"
        }
    ],
    "response_metadata": {
        "next_cursor": ""  # Empty cursor indicates no more pages
    }
}

# Thread HTML response
THREAD_HTML_V2 = {
    "html": "<h1>Document Title</h1><p>Content</p>",
    "response_metadata": {
        "next_cursor": "next_page_token"
    }
}

# Multiple threads response
MULTIPLE_THREADS_V2 = {
    "THREAD1": BASIC_THREAD_V2["thread"],
    "THREAD2": {
        "author_id": "USER456",
        "created_usec": 1609459200000000,
        "id": "THREAD2",
        "is_template": False,
        "link": "https://test.quip.com/def456",
        "owning_company_id": "COMPANY1", 
        "secret_path": "def456",
        "title": "Another Document",
        "type": "DOCUMENT",
        "updated_usec": 1609545600000000,
        "sharing": {
            "company_id": "COMPANY1",
            "company_mode": "VIEW"
        }
    }
}

# Test cases mapping
THREAD_V2_TEST_CASES = [
    ("basic_thread", BASIC_THREAD_V2),
    ("thread_folders", THREAD_FOLDERS_V2),
    ("thread_html", THREAD_HTML_V2),
    ("multiple_threads", MULTIPLE_THREADS_V2)
]
