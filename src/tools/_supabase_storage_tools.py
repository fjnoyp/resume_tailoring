"""
Private Supabase Storage Implementation

Low-level storage operations for Supabase. This module should NOT be imported
directly by nodes or other application code. Use StateStorageManager instead.
"""

import logging
import os
from typing import Optional
from supabase import create_client, Client
import asyncio

# Private module - should only be used by StateStorageManager
supabase_client: Client = create_client(
    os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY")
)

bucket_name = "temp"


async def _read_file_from_bucket(file_path: str) -> Optional[bytes]:
    """
    Retrieves the raw bytes of a file from a specific Supabase storage path.

    PRIVATE: Use StateStorageManager.read_file() instead.

    Args:
        file_path: Full path (including filename) within the bucket.

    Returns:
        The file content as bytes if found, None otherwise
    """
    try:
        response = await asyncio.to_thread(
            lambda: supabase_client.storage.from_(bucket_name).download(file_path)
        )
        logging.debug(f"[Storage] Downloaded file: {file_path}")
        return response
    except Exception as e:
        logging.debug(f"[Storage] Error retrieving file {file_path}: {e}")
        return None


async def _list_files_in_bucket(path: str = "") -> Optional[list]:
    """
    Lists all files and folders at a given Supabase storage path.

    PRIVATE: Use StateStorageManager.list_files() instead.

    Args:
        path: Folder or subdirectory path (default is root).

    Returns:
        A list of file details if successful, None otherwise
    """
    try:
        response = await asyncio.to_thread(
            lambda: supabase_client.storage.from_(bucket_name).list(path)
        )
        logging.debug(f"[Storage] Listed files in: {path}")
        return response
    except Exception as e:
        logging.debug(f"[Storage] Error listing files in {path}: {e}")
        return None


async def _upload_file_to_bucket(file_path: str, file_content: str) -> Optional[dict]:
    """
    Uploads or overwrites a file in a Supabase storage specified path.

    PRIVATE: Use StateStorageManager.save_file() instead.

    Args:
        file_path: Full destination path (including filename).
        file_content: String content to upload (UTF-8 encoded).

    Returns:
        The upload response dict if successful, None otherwise
    """
    try:
        response = await asyncio.to_thread(
            lambda: supabase_client.storage.from_(bucket_name).upload(
                file_path, file_content.encode("utf-8"), {"upsert": "true"}
            )
        )
        logging.debug(f"[Storage] Uploaded file: {file_path}")
        return response
    except Exception as e:
        logging.debug(f"[Storage] Error uploading file {file_path}: {e}")
        return None


async def _delete_file_from_bucket(file_path: str) -> Optional[dict]:
    """
    Permanently deletes a file from a given Supabase storage path.

    PRIVATE: Use StateStorageManager.delete_file() instead.

    Args:
        file_path: Full path (including filename) of the file to delete.

    Returns:
        The delete response dict if successful, None otherwise
    """
    try:
        response = await asyncio.to_thread(
            lambda: supabase_client.storage.from_(bucket_name).remove([file_path])
        )
        logging.debug(f"[Storage] Deleted file: {file_path}")
        return response
    except Exception as e:
        logging.debug(f"[Storage] Error deleting file {file_path}: {e}")
        return None
