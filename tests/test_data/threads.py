"""Test data for thread-related API responses"""

# Simple document thread
SIMPLE_THREAD = {
    "thread": {
        "author_id": "USER123",
        "thread_class": "document",
        "owning_company_id": "COMPANY1",
        "id": "THREAD123",
        "created_usec": 1609459200000000,
        "updated_usec": 1609545600000000,
        "title": "Project Notes",
        "link": "https://test.quip.com/docs/notes",
        "document_id": "DOC123",
        "type": "document",
        "is_template": False
    },
    "html": "<h1>Project Notes</h1><p>Initial planning</p>",
    "user_ids": ["USER123"],
    "shared_folder_ids": ["FOLDER1"],
    "access_levels": {
        "USER123": {"access_level": "OWN"}
    }
}

# Complex thread with multiple users and content
COMPLEX_THREAD = {
    "thread": {
        "author_id": "USER456",
        "thread_class": "document",
        "owning_company_id": "COMPANY1",
        "id": "THREAD456",
        "created_usec": 1609459200000000,
        "updated_usec": 1609545600000000,
        "title": "Team Roadmap",
        "link": "https://test.quip.com/docs/roadmap",
        "document_id": "DOC456",
        "type": "document",
        "is_template": False
    },
    "html": "<h1>Q1 Roadmap</h1><table><tr><td>Feature</td><td>Status</td></tr></table>",
    "user_ids": ["USER456", "USER789"],
    "shared_folder_ids": ["FOLDER1", "FOLDER2"],
    "expanded_user_ids": ["USER456", "USER789"],
    "invited_user_emails": ["new@test.com"],
    "access_levels": {
        "USER456": {"access_level": "OWN"},
        "USER789": {"access_level": "EDIT"}
    }
}

# Test cases mapping
THREAD_TEST_CASES = [
    ("simple_thread", SIMPLE_THREAD),
    ("complex_thread", COMPLEX_THREAD)
]
