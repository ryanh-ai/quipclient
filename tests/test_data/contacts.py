"""Test data for contacts-related API responses"""

# Basic contacts list
BASIC_CONTACTS = {
    "contacts": [
        {"id": "USER1", "name": "Contact 1"},
        {"id": "USER2", "name": "Contact 2"}
    ]
}

# Empty contacts list
EMPTY_CONTACTS = {
    "contacts": []
}

# Test cases mapping
CONTACTS_TEST_CASES = [
    ("basic_contacts", BASIC_CONTACTS),
    ("empty_contacts", EMPTY_CONTACTS)
]
