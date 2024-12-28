"""Test data for batch folder operations"""

# Simple folders test case
SIMPLE_FOLDERS = {
    "FOLDER1": {"folder": {"id": "FOLDER1", "title": "Test 1", "type": "folder"}},
    "FOLDER2": {"folder": {"id": "FOLDER2", "title": "Test 2", "type": "folder"}}
}

# Empty folders test case
EMPTY_FOLDERS = {}

# Test cases mapping
BATCH_FOLDER_TEST_CASES = [
    ("simple_folders", SIMPLE_FOLDERS),
    ("empty_folders", EMPTY_FOLDERS)
]
