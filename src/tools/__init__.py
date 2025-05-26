"""
Storage Tools Package

Public interfaces for storage operations. Use these imports to ensure
you're using the correct abstraction level.
"""

# Primary storage interface - use this for all storage operations
from .state_storage_manager import (
    StateStorageManager,
    StateLoadMode,
    StateLoadResult,
    load_resume_tailoring_data,
    load_user_profile_data,
    save_processing_result,
)

# Path management utilities
from .file_path_manager import (
    get_file_paths,
    UserFilePaths,
    get_field_to_path_mapping,
)

# Agent tools for LangChain workflows
from .storage_tools import storage_tools

# Other utilities
from .parse_pdf_tool import parse_pdf

# Note: _supabase_storage_tools is private and should not be imported directly
# Use StateStorageManager instead for all storage operations

__all__ = [
    # Storage Manager (primary interface)
    "StateStorageManager",
    "StateLoadMode",
    "StateLoadResult",
    "load_resume_tailoring_data",
    "load_user_profile_data",
    "save_processing_result",
    # Path Management
    "get_file_paths",
    "UserFilePaths",
    "get_field_to_path_mapping",
    # Agent Tools
    "storage_tools",
    # Utilities
    "parse_pdf",
]
