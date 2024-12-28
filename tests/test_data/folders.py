"""Folder-related test data"""

FOLDERS_DATA = {
    "folder1": {
        "folder": {
            "creator_id": "NOP012qrs",
            "folder_type": "private",
            "inherit_mode": "reset",
            "id": "KLM789nop",
            "created_usec": 1510251981120743,
            "updated_usec": 1732837192184612,
            "link": "https://example.com/KLM789nop",
            "title": "Mock Folder 1"
        },
        "member_ids": ["NOP012qrs"],
        "children": [
            {"thread_id": "QRS345tuv"},
            {"folder_id": "TUV678wxy"}
        ]
    },
    "folder2": {
        "folder": {
            "creator_id": "NOP012qrs",
            "folder_type": "shared",
            "inherit_mode": "inherit",
            "id": "WXY901zab",
            "created_usec": 1510251981120743,
            "updated_usec": 1732837192184612,
            "link": "https://example.com/WXY901zab",
            "title": "Mock Folder 2"
        },
        "member_ids": ["NOP012qrs"],
        "children": [
            {"thread_id": "CDE234fgh"},
            {"folder_id": "FGH567ijk"}
        ]
    }
}
