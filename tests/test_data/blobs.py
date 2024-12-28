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


