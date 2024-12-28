"""Thread-related test data"""

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
        "html": "<h1>Mock Content 2</h1>",
        "user_ids": ["LMN123opq"],
        "shared_folder_ids": [],
        "access_levels": {"LMN123opq": {"access_level": "OWN"}}
    }
}
