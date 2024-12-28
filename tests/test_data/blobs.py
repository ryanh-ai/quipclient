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

# Batch test data
FOLDERS_BATCH = {
    "FOLDER1": {"folder": {"id": "FOLDER1", "title": "Test 1"}},
    "FOLDER2": {"folder": {"id": "FOLDER2", "title": "Test 2"}}
}

THREADS_BATCH = {
    "THREAD1": {"thread": {"id": "THREAD1", "title": "Thread 1"}},
    "THREAD2": {"thread": {"id": "THREAD2", "title": "Thread 2"}}
}

# Batch test cases
BATCH_TEST_CASES = [
    ("folders_batch", FOLDERS_BATCH),
    ("threads_batch", THREADS_BATCH)
]
