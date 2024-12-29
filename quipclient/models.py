"""Data models for Quip API responses."""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any
from datetime import datetime
from enum import Enum

class ThreadType(str, Enum):
    """Types of Quip threads"""
    DOCUMENT = "DOCUMENT"
    SPREADSHEET = "SPREADSHEET" 
    SLIDES = "SLIDES"
    CHAT = "CHAT"

class FolderType(str, Enum):
    """Types of Quip folders"""
    PRIVATE = "PRIVATE"
    SHARED = "SHARED"

@dataclass
class ThreadMetadata:
    """Metadata about a Quip thread"""
    thread_id: str
    title: str
    thread_type: ThreadType
    updated_usec: int
    author_id: Optional[str] = None
    created_usec: Optional[int] = None
    is_deleted: bool = False
    folder_ids: Set[str] = field(default_factory=set)
    html_loaded: bool = False
    owning_company_id: Optional[str] = None
    link: Optional[str] = None
    is_template: bool = False
    sharing: Optional[Dict[str, Any]] = None

    @classmethod
    def from_v2_response(cls, thread_data: Dict[str, Any]) -> 'ThreadMetadata':
        """Create ThreadMetadata from v2 API response"""
        thread = thread_data['thread']
        return cls(
            thread_id=thread['id'],
            title=thread['title'],
            thread_type=ThreadType(thread['type']),
            updated_usec=thread['updated_usec'],
            created_usec=thread.get('created_usec'),
            author_id=thread.get('author_id'),
            is_deleted=thread.get('is_deleted', False),
            owning_company_id=thread.get('owning_company_id'),
            link=thread.get('link'),
            is_template=thread.get('is_template', False),
            sharing=thread.get('sharing'),
            html_loaded=False,
            folder_ids=set()
        )

    @property
    def last_updated(self) -> datetime:
        """Convert updated_usec to datetime"""
        return datetime.fromtimestamp(self.updated_usec / 1_000_000)

    @property
    def created_at(self) -> Optional[datetime]:
        """Convert created_usec to datetime if available"""
        if self.created_usec:
            return datetime.fromtimestamp(self.created_usec / 1_000_000)
        return None

@dataclass
class FolderMetadata:
    """Metadata about a Quip folder"""
    folder_id: str
    title: str
    folder_type: FolderType
    created_usec: int
    updated_usec: int
    creator_id: str
    parent_id: Optional[str] = None
    color: Optional[str] = None
    member_ids: Set[str] = field(default_factory=set)
    inherit_mode: str = "inherit"
    link: Optional[str] = None

    @classmethod
    def from_response(cls, folder_data: Dict[str, Any]) -> 'FolderMetadata':
        """Create FolderMetadata from API response"""
        folder = folder_data['folder']
        return cls(
            folder_id=folder['id'],
            title=folder['title'],
            folder_type=FolderType(folder['folder_type'].upper()),
            created_usec=folder['created_usec'],
            updated_usec=folder['updated_usec'],
            creator_id=folder['creator_id'],
            parent_id=folder.get('parent_id'),
            color=folder.get('color'),
            member_ids=set(folder_data.get('member_ids', [])),
            inherit_mode=folder.get('inherit_mode', 'inherit'),
            link=folder.get('link')
        )

    @property
    def last_updated(self) -> datetime:
        """Convert updated_usec to datetime"""
        return datetime.fromtimestamp(self.updated_usec / 1_000_000)

    @property
    def created_at(self) -> datetime:
        """Convert created_usec to datetime"""
        return datetime.fromtimestamp(self.created_usec / 1_000_000)

@dataclass
class FolderNode:
    """Node in the folder tree structure"""
    metadata: FolderMetadata
    children: Dict[str, 'FolderNode'] = field(default_factory=dict)
    threads: Set[str] = field(default_factory=set)
    parent: Optional['FolderNode'] = None
    depth: int = 0

    def add_child(self, child: 'FolderNode') -> None:
        """Add a child folder node"""
        child.parent = self
        child.depth = self.depth + 1
        self.children[child.metadata.folder_id] = child

    def add_thread(self, thread_id: str) -> None:
        """Add a thread to this folder"""
        self.threads.add(thread_id)

    def get_path(self) -> List[str]:
        """Get the path of folder IDs from root to this node"""
        if self.parent is None:
            return [self.metadata.folder_id]
        return self.parent.get_path() + [self.metadata.folder_id]

    def get_all_threads(self) -> Set[str]:
        """Get all threads in this folder and subfolders"""
        result = set(self.threads)
        for child in self.children.values():
            result.update(child.get_all_threads())
        return result
