"""Test data for folder-related API responses"""

# Private folder
PRIVATE_FOLDER = {
    "folder": {
        "creator_id": "USER123",
        "folder_type": "private",
        "inherit_mode": "reset",
        "id": "PRIV_FOLD",
        "created_usec": 1609459200000000,
        "updated_usec": 1609545600000000,
        "link": "https://test.quip.com/folders/private",
        "title": "Personal Files"
    },
    "member_ids": ["USER123"],
    "children": [
        {"thread_id": "THREAD1"},
        {"folder_id": "SUBFOLD1"}
    ]
}

# Shared folder
SHARED_FOLDER = {
    "folder": {
        "creator_id": "USER123",
        "folder_type": "shared",
        "inherit_mode": "inherit",
        "color": "blue",
        "id": "SHARE_FOLD",
        "created_usec": 1609459200000000,
        "updated_usec": 1609545600000000,
        "link": "https://test.quip.com/folders/shared",
        "title": "Team Projects"
    },
    "member_ids": ["USER123", "USER456", "USER789"],
    "children": [
        {"thread_id": "THREAD2"},
        {"thread_id": "THREAD3"},
        {"folder_id": "SUBFOLD2"}
    ]
}

# Test cases mapping
FOLDER_TEST_CASES = [
    ("private_folder", PRIVATE_FOLDER),
    ("shared_folder", SHARED_FOLDER)
]
