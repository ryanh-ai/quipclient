"""Test data for blob-related API responses"""

# Sample PNG image header bytes
PNG_HEADER = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x04\x00\x00\x00\x03'
    b'\xda\x08\x06\x00\x00\x00\t\x1f*D\x00\x00\x0c?iCCPICC Profile'
)

# Test cases with binary content and metadata
BLOB_TEST_CASES = [
    ("text_blob", {
        "thread_id": "THREAD1",
        "blob_id": "abc123",
        "content": b"This is a sample text file content.\nIt has multiple lines.\n",
        "content_type": "text/plain",
        "content_length": 48
    }),
    ("image_blob", {
        "thread_id": "THREAD2", 
        "blob_id": "def456",
        "content": PNG_HEADER + b'\x00' * 1024,  # Pad with nulls to simulate image data
        "content_type": "image/png",
        "content_length": 1024 + len(PNG_HEADER)
    }),
    ("pdf_blob", {
        "thread_id": "THREAD3",
        "blob_id": "ghi789", 
        "content": b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n" + b'\x00' * 512,  # Basic PDF header
        "content_type": "application/pdf",
        "content_length": 518
    })
]

