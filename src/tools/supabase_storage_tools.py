import logging
import os
from typing import Optional
from dataclasses import dataclass
from supabase import create_client, Client
import io
import asyncio

supabase_client: Client = create_client(
    os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY")
)

bucket_name = "temp"


@dataclass(frozen=True)
class UserFilePaths:
    """
    Typed container for all user file paths in Supabase Storage.
    Provides type safety and prevents magic string usage.
    """

    user_id: str
    job_id: str

    @property
    def user_full_resume_path(self) -> str:
        """Path to user's complete resume with all details"""
        return f"{self.user_id}/FULL_RESUME.md"

    @property
    def original_resume_path(self) -> str:
        """Path to user's base resume"""
        return f"{self.user_id}/ORIGINAL_RESUME.md"

    @property
    def job_description_path(self) -> str:
        """Path to job posting content"""
        return f"{self.user_id}/{self.job_id}/JOB_DESCRIPTION.md"

    @property
    def job_strategy_path(self) -> str:
        """Path to job analysis and strategy document"""
        return f"{self.user_id}/{self.job_id}/JOB_STRATEGY.md"

    @property
    def tailored_resume_path(self) -> str:
        """Path to customized resume for this job"""
        return f"{self.user_id}/{self.job_id}/TAILORED_RESUME.md"

    @property
    def recruiter_feedback_path(self) -> str:
        """Path to recruiter evaluation document"""
        return f"{self.user_id}/{self.job_id}/RECRUITER_FEEDBACK.md"

    @property
    def cover_letter_path(self) -> str:
        """Path to cover letter for this job"""
        return f"{self.user_id}/{self.job_id}/COVER_LETTER.md"

    def custom_file_path(self, filename: str) -> str:
        """Path for any custom file in the job directory"""
        return f"{self.user_id}/{self.job_id}/{filename}"

    @property
    def other_files_path(self) -> str:
        """Path for any other file in the job directory"""
        return f"{self.user_id}/{self.job_id}/[file_name]"


def get_file_paths(user_id: str, job_id: str) -> UserFilePaths:
    """
    Returns typed file paths for user and job.

    Args:
        user_id: Unique user identifier
        job_id: Unique job identifier

    Returns:
        UserFilePaths object with type-safe path properties
    """
    return UserFilePaths(user_id=user_id, job_id=job_id)


async def read_file_from_bucket(file_path: str) -> Optional[bytes]:
    """
    Retrieves the raw bytes of a file from a specific Supabase storage path.

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
    Lists all files and folders at a given Supabase storage path.

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
    Uploads or overwrites a file in a Supabase storage specified path.

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
        logging.debug(response)
        return response
    except Exception as e:
        print(f"Error uploading file to bucket: {e}")
        return None


async def delete_file_from_bucket(file_path: str) -> Optional[dict]:
    """
    Permanently deletes a file from a given Supabase storage path.

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
    delete_file_from_bucket,
]
