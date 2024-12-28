"""User-related test data"""

# Basic user structure
USER_DATA = {
    "name": "Mock User",
    "id": "test_user",
    "is_robot": False,
    "affinity": 0.0
}

# User with just emails added
USER_WITH_EMAILS = {
    "name": "Mock Email User",
    "emails": ["user2@example.com"],
    "id": "email_user",
    "is_robot": False,
    "affinity": 0.0
}

# Full authenticated user structure
AUTHENTICATED_USER_DATA = {
    "name": "Mock Auth User",
    "emails": ["user@example.com"],
    "id": "auth_user",
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
