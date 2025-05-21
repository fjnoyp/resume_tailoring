import logging
import os
from typing import Optional
from supabase import create_client, Client
import io
import asyncio

supabase_client: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

bucket_name = "temp"

def get_user_files_paths(user_id: str, job_id: str) -> dict[str, str]:
    """
    Returns the standard storage paths for all main user/job-related files in Supabase. Use to get canonical file locations for a user and job, regardless of file existence.

    Args:
        user_id: Unique user identifier (from context).
        job_id: Unique job identifier (from context).
    
    Returns:
        Dict with full paths for resume, job description, job strategy, tailored resume, original resume, recruiter feedback, cover letter, and any other files (with a placeholder for the file name).
    """

    response = {
        "user_full_resume_path": f"{user_id}/FULL_RESUME.md",
        "original_resume_path": f"{user_id}/ORIGINAL_RESUME.md",
        "job_description_path": f"{user_id}/{job_id}/JOB_DESCRIPTION.md",
        "job_strategy_path": f"{user_id}/{job_id}/JOB_STRATEGY.md",
        "tailored_resume_path": f"{user_id}/{job_id}/TAILORED_RESUME.md",
        "recruiter_feedback_path": f"{user_id}/{job_id}/RECRUITER_FEEDBACK.md",
        "cover_letter_path": f"{user_id}/{job_id}/COVER_LETTER.md",
        "path for any other files": f"{user_id}/{job_id}/[file_name]"
    }

    return response

async def read_file_from_bucket(file_path: str) -> Optional[bytes]:
    """
    Retrieves the raw bytes of a file from a specific Supabase storage path. Use to read any file's contents if you know its location.
    
    Args:
        file_path: Full path (including filename) within the bucket.
    
    Returns:
        The file content as bytes if found, None otherwise
    """
    try:
        response = await asyncio.to_thread(
            lambda: supabase_client.storage.from_(bucket_name).download(file_path)
        )
        logging.debug(response)
        return response
    except Exception as e:
        print(f"Error retrieving file from bucket: {e}")
        return None

async def list_files_in_bucket(path: str = "") -> Optional[list]:
    """
    Lists all files and folders at a given Supabase storage path. Use to browse or verify available files in a bucket or folder. Only use this tool if other tools fail and you need to list files in a specific folder.

    Note: Always prefer to use the "get_user_files_paths" tool to get the full paths for all main user/job-related files in Supabase.
    
    Args:
        path: Folder or subdirectory path (default is root).
    
    Returns:
        A list of file details if successful, None otherwise
    """
    try:
        response = await asyncio.to_thread(
            lambda: supabase_client.storage.from_(bucket_name).list(path)
        )
        logging.debug(response)
        return response
    except Exception as e:
        print(f"Error listing files in bucket: {e}")
        return None

async def upload_file_to_bucket(file_path: str, file_content: str) -> Optional[dict]:
    """
    Uploads or overwrites a file in a Supabase storage specified path. Use to save or update any file's contents.
    
    Args:
        file_path: Full destination path (including filename).
        file_content: String content to upload (UTF-8 encoded).
    
    Returns:
        The upload response dict if successful, None otherwise
    """
    try:
        response = await asyncio.to_thread(
            lambda: supabase_client.storage.from_(bucket_name).upload(
                file_path,
                file_content.encode("utf-8"),
                {"upsert": "true"}
            )
        )
        logging.debug(response)
        return response
    except Exception as e:
        print(f"Error uploading file to bucket: {e}")
        return None

async def delete_file_from_bucket(file_path: str) -> Optional[dict]:
    """
    Permanently deletes a file from a given Supabase storage path. Use to remove files that are no longer needed.
    
    Args:
        file_path: Full path (including filename) of the file to delete.
    
    Returns:
        The delete response dict if successful, None otherwise
    """
    try:
        response = await asyncio.to_thread(
            lambda: supabase_client.storage.from_(bucket_name).remove([file_path])
        )
        logging.debug(response)
        return response
    except Exception as e:
        print(f"Error deleting file from bucket: {e}")
        return None

supabase_storage_tools = [
    read_file_from_bucket,
    list_files_in_bucket,
    upload_file_to_bucket,
    delete_file_from_bucket
]
