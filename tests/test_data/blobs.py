"""Test data for blob-related API responses"""

"""Test data for blob-related API responses"""

# Test cases with binary content and metadata
BLOB_TEST_CASES = [
    ("text_blob", {
        "thread_id": "THREAD1",
        "blob_id": "abc123",
        "content": b"Simple text content",
        "content_type": "text/plain"
    }),
    ("image_blob", {
        "thread_id": "THREAD2", 
        "blob_id": "def456",
        "content": b"\x89PNG\r\n\x1a\n",
        "content_type": "image/png"
    })
]


