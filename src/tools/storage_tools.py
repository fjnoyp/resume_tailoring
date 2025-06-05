"""
Storage Tools for LangChain Agents

Provides LangChain-compatible tools that use StateDataManager as the backend.
These tools can be used by agents that need storage operations.
"""

from langchain_core.tools import tool
from typing import Optional, List
from src.tools.state_data_manager import StateDataManager


@tool
async def read_file_from_bucket(file_path: str) -> Optional[str]:
    """
    Retrieves the content of a file from storage.

    Args:
        file_path: Full path (including filename) within the storage bucket.

    Returns:
        The file content as string if found, None otherwise
    """
    return await StateDataManager._load_file_content(file_path)


@tool
async def upload_file_to_bucket(file_path: str, file_content: str) -> str:
    """
    Uploads or overwrites a file in storage.

    Args:
        file_path: Full destination path (including filename).
        file_content: String content to upload.

    Returns:
        Success message or error message
    """
    from src.tools._supabase_storage_tools import _upload_file_to_bucket

    result = await _upload_file_to_bucket(file_path, file_content)
    if result:
        return f"Successfully uploaded file to {file_path}"
    else:
        return f"Failed to upload file to {file_path}"


@tool
async def list_files_in_bucket(path: str = "") -> str:
    """
    Lists all files and folders at a given storage path.

    Args:
        path: Folder or subdirectory path (default is root).

    Returns:
        A formatted string listing the files
    """
    from src.tools._supabase_storage_tools import _list_files_in_bucket

    files_data = await _list_files_in_bucket(path)
    if not files_data:
        return f"No files found in path: {path}"

    file_list = []
    for file_data in files_data:
        if isinstance(file_data, dict) and file_data.get("name"):
            file_list.append(file_data["name"])

    if file_list:
        return f"Files in {path}: {', '.join(file_list)}"
    else:
        return f"No files found in path: {path}"


@tool
async def delete_file_from_bucket(file_path: str) -> str:
    """
    Permanently deletes a file from storage.

    Args:
        file_path: Full path (including filename) of the file to delete.

    Returns:
        Success message or error message
    """
    from src.tools._supabase_storage_tools import _delete_file_from_bucket

    result = await _delete_file_from_bucket(file_path)
    if result:
        return f"Successfully deleted file: {file_path}"
    else:
        return f"Failed to delete file: {file_path}"


# List of storage tools for agent use
storage_tools = [
    read_file_from_bucket,
    upload_file_to_bucket,
    list_files_in_bucket,
    delete_file_from_bucket,
]
