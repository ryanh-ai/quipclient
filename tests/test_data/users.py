"""User-related test data"""

USER_DATA = {
    "name": "Mock User",
    "id": "test_user",
    "is_robot": False,
    "affinity": 0.0
}

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
