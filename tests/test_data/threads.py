"""Thread-related test data"""

# Basic thread structure
THREAD_DATA = {
    "thread": {
        "author_id": "ABC123xyz",
        "thread_class": "document",
        "owning_company_id": "XYZ789abc",
        "id": "test123",
        "created_usec": 1735232430682856,
        "updated_usec": 1735232468086554,
        "title": "Mock Document",
        "link": "https://example.com/DEF456uvw",
        "document_id": "GHI789rst",
        "type": "document",
        "is_template": False,
        "is_deleted": False
    }
}

THREADS_DATA = {
    # Thread with basic HTML content
    "thread1": {
        "thread": {
            "author_id": "LMN123opq",
            "thread_class": "document",
            "owning_company_id": "OPQ456rst",
            "id": "IJK890lmn",
            "created_usec": 1735232430682856,
            "updated_usec": 1735232468086554,
            "title": "Mock Thread 1",
            "link": "https://example.com/IJK890lmn",
            "document_id": "RST789uvw",
            "type": "document",
            "is_template": False
        },
        "html": "<h1>Mock Content 1</h1>",
        "user_ids": ["LMN123opq"],
        "shared_folder_ids": [],
        "access_levels": {"LMN123opq": {"access_level": "OWN"}}
    },
    # Thread with complex HTML including tables
    "thread2": {
        "thread": {
            "author_id": "LMN123opq",
            "thread_class": "document",
            "owning_company_id": "OPQ456rst",
            "id": "UVW012xyz",
            "created_usec": 1735232430682856,
            "updated_usec": 1735232468086554,
            "title": "Mock Thread 2",
            "link": "https://example.com/UVW012xyz",
            "document_id": "XYZ345abc",
            "type": "document",
            "is_template": False
        },
        "html": "<h1>Complex Document</h1><table><tr><td>Cell 1</td><td>Cell 2</td></tr></table>",
        "user_ids": ["LMN123opq", "ABC123xyz"],
        "shared_folder_ids": ["FOLDER1", "FOLDER2"],
        "expanded_user_ids": ["LMN123opq", "ABC123xyz"],
        "invited_user_emails": ["user1@example.com", "user2@example.com"],
        "access_levels": {
            "LMN123opq": {"access_level": "OWN"},
            "ABC123xyz": {"access_level": "EDIT"}
        }
    },
    # Thread that's a template
    "thread3": {
        "thread": {
            "author_id": "LMN123opq",
            "thread_class": "document",
            "owning_company_id": "OPQ456rst",
            "id": "TEMPLATE123",
            "created_usec": 1735232430682856,
            "updated_usec": 1735232468086554,
            "title": "Template Document",
            "link": "https://example.com/TEMPLATE123",
            "document_id": "TEMPL345abc",
            "type": "document",
            "is_template": True
        },
        "html": "<h1>Template Content</h1>",
        "user_ids": ["LMN123opq"],
        "shared_folder_ids": [],
        "access_levels": {"LMN123opq": {"access_level": "OWN"}}
    }
}
