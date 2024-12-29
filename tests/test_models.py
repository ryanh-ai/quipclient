"""Tests for Quip data models"""

import pytest
from datetime import datetime
from quipclient.models import (
    ThreadMetadata, 
    FolderMetadata,
    FolderNode,
    ThreadType,
    FolderType
)

@pytest.fixture
def sample_thread_v2():
    """Sample v2 API thread response"""
    return {
        'thread': {
            'author_id': 'USER123',
            'created_usec': 1672603200000000,  # 2023-01-01 12:00:00 UTC
            'id': 'THREAD123',
            'is_template': False,
            'link': 'https://quip.com/abc123',
            'owning_company_id': 'COMPANY123',
            'title': 'Test Document',
            'type': 'DOCUMENT',
            'updated_usec': 1704110400000000,  # 2024-01-01 12:00:00 UTC
            'sharing': {
                'company_mode': 'VIEW'
            }
        }
    }

@pytest.fixture
def sample_folder():
    """Sample API folder response"""
    return {
        'folder': {
            'id': 'FOLDER123',
            'title': 'Test Folder',
            'folder_type': 'shared',
            'created_usec': 1672603200000000,  # 2023-01-01 12:00:00 UTC
            'updated_usec': 1704110400000000,  # 2024-01-01 12:00:00 UTC
            'creator_id': 'USER123',
            'color': 'blue',
            'inherit_mode': 'inherit',
            'link': 'https://quip.com/folder/abc123'
        },
        'member_ids': ['USER123', 'USER456']
    }

def test_thread_metadata_from_v2(sample_thread_v2):
    """Test creating ThreadMetadata from v2 API response"""
    metadata = ThreadMetadata.from_v2_response(sample_thread_v2)
    
    assert metadata.thread_id == 'THREAD123'
    assert metadata.title == 'Test Document'
    assert metadata.thread_type == ThreadType.DOCUMENT
    assert metadata.author_id == 'USER123'
    assert metadata.created_usec == 1672603200000000
    assert metadata.updated_usec == 1704110400000000
    assert metadata.owning_company_id == 'COMPANY123'
    assert metadata.link == 'https://quip.com/abc123'
    assert not metadata.is_template
    assert not metadata.is_deleted
    assert not metadata.html_loaded
    assert metadata.sharing == {'company_mode': 'VIEW'}
    assert len(metadata.folder_ids) == 0

def test_thread_metadata_datetime_properties(sample_thread_v2):
    """Test datetime conversion properties"""
    metadata = ThreadMetadata.from_v2_response(sample_thread_v2)
    
    assert isinstance(metadata.last_updated, datetime)
    assert metadata.last_updated.year == 2024
    assert metadata.last_updated.month == 1
    assert metadata.last_updated.day == 1

    assert isinstance(metadata.created_at, datetime)
    assert metadata.created_at.year == 2023
    assert metadata.created_at.month == 1
    assert metadata.created_at.day == 1

def test_folder_metadata_from_response(sample_folder):
    """Test creating FolderMetadata from API response"""
    metadata = FolderMetadata.from_response(sample_folder)
    
    assert metadata.folder_id == 'FOLDER123'
    assert metadata.title == 'Test Folder'
    assert metadata.folder_type == FolderType.SHARED
    assert metadata.creator_id == 'USER123'
    assert metadata.created_usec == 1672603200000000
    assert metadata.updated_usec == 1704110400000000
    assert metadata.color == 'blue'
    assert metadata.inherit_mode == 'inherit'
    assert metadata.link == 'https://quip.com/folder/abc123'
    assert len(metadata.member_ids) == 2
    assert 'USER123' in metadata.member_ids
    assert 'USER456' in metadata.member_ids

def test_folder_metadata_datetime_properties(sample_folder):
    """Test datetime conversion properties"""
    metadata = FolderMetadata.from_response(sample_folder)
    
    assert isinstance(metadata.last_updated, datetime)
    assert metadata.last_updated.year == 2024
    assert metadata.last_updated.month == 1
    assert metadata.last_updated.day == 1

    assert isinstance(metadata.created_at, datetime)
    assert metadata.created_at.year == 2023
    assert metadata.created_at.month == 1
    assert metadata.created_at.day == 1

def test_folder_node_tree():
    """Test FolderNode tree operations"""
    # Create root folder
    root_data = {
        'folder': {
            'id': 'ROOT',
            'title': 'Root',
            'folder_type': 'private',
            'created_usec': 1672531200000000,
            'updated_usec': 1704067200000000,
            'creator_id': 'USER123'
        },
        'member_ids': ['USER123']
    }
    root = FolderNode(FolderMetadata.from_response(root_data))
    
    # Create child folder
    child_data = {
        'folder': {
            'id': 'CHILD',
            'title': 'Child',
            'folder_type': 'shared',
            'created_usec': 1672531200000000,
            'updated_usec': 1704067200000000,
            'creator_id': 'USER123'
        },
        'member_ids': ['USER123']
    }
    child = FolderNode(FolderMetadata.from_response(child_data))
    
    # Add child to root
    root.add_child(child)
    assert child.parent == root
    assert child.depth == 1
    assert root.children['CHILD'] == child
    
    # Add threads
    root.add_thread('THREAD1')
    child.add_thread('THREAD2')
    
    # Test path
    assert root.get_path() == ['ROOT']
    assert child.get_path() == ['ROOT', 'CHILD']
    
    # Test getting all threads
    assert root.get_all_threads() == {'THREAD1', 'THREAD2'}
    assert child.get_all_threads() == {'THREAD2'}
