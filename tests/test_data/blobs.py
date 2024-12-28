"""Test data for blob-related API responses"""

# Simple text blob
SIMPLE_BLOB = {
    "content": b"Simple text content",
    "response": {
        "id": "BLOB123",
        "name": "simple.txt",
        "hash": "abc123",
        "thread_id": "THREAD1"
    }
}

# Binary blob
BINARY_BLOB = {
    "content": b"\x89PNG\r\n\x1a\n",
    "response": {
        "id": "BLOB456",
        "name": "test.png",
        "hash": "def456",
        "thread_id": "THREAD1"
    }
}

# Test cases mapping
BLOB_TEST_CASES = [
    ("simple_blob", SIMPLE_BLOB),
    ("binary_blob", BINARY_BLOB)
]

# Batch folder test cases
BATCH_FOLDER_TEST_CASES = [
    ("simple_folders", {
        "FOLDER1": {"folder": {"id": "FOLDER1", "title": "Test 1", "type": "folder"}},
        "FOLDER2": {"folder": {"id": "FOLDER2", "title": "Test 2", "type": "folder"}}
    }),
    ("empty_folders", {})
]

# Batch thread test cases
BATCH_THREAD_TEST_CASES = [
    ("simple_threads", {
        "THREAD1": {"thread": {"id": "THREAD1", "title": "Thread 1", "type": "document"}},
        "THREAD2": {"thread": {"id": "THREAD2", "title": "Thread 2", "type": "document"}}
    }),
    ("empty_threads", {})
]

