"""Test data for user-related API responses"""

# Basic user info (minimal response)
BASIC_USER = {
    "name": "John Smith",
    "id": "SMITH123",
    "is_robot": False,
    "affinity": 0.0
}

# User with email info
EMAIL_USER = {
    "name": "Jane Doe",
    "emails": ["jane.doe@test.com"],
    "id": "DOE456",
    "is_robot": False,
    "affinity": 0.0
}

# Full authenticated user data
AUTH_USER = {
    "name": "Admin User",
    "emails": ["admin@test.com"],
    "id": "ADMIN789",
    "is_robot": False,
    "affinity": 0.0,
    "desktop_folder_id": "DESK123",
    "archive_folder_id": "ARCH456", 
    "starred_folder_id": "STAR789",
    "private_folder_id": "PRIV012",
    "trash_folder_id": "TRASH345",
    "shared_folder_ids": ["SHARED1", "SHARED2"],
    "group_folder_ids": ["GROUP1"],
    "subdomain": "test",
    "url": "https://test.quip.com"
}

# Test cases mapping
USER_TEST_CASES = [
    ("basic_user", BASIC_USER),
    ("email_user", EMAIL_USER), 
    ("auth_user", AUTH_USER)
]
