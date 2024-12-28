"""Test data for messages-related API responses"""

# Basic message list
BASIC_MESSAGES = [
    {
        "id": "MSG1",
        "author_id": "USER1",
        "text": "Hello team",
        "created_usec": 1609459200000000
    },
    {
        "id": "MSG2", 
        "author_id": "USER2",
        "text": "Hi there",
        "created_usec": 1609459300000000
    }
]

# Messages with attachments
MESSAGES_WITH_ATTACHMENTS = [
    {
        "id": "MSG3",
        "author_id": "USER1",
        "text": "See attached",
        "created_usec": 1609459400000000,
        "files": [
            {"hash": "abc123", "name": "doc.pdf"}
        ]
    }
]

# Test cases mapping
MESSAGES_TEST_CASES = [
    ("basic_messages", BASIC_MESSAGES),
    ("messages_with_attachments", MESSAGES_WITH_ATTACHMENTS)
]
