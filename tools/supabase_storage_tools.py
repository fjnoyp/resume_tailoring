import logging
import os
from typing import Optional
from supabase import create_client, Client
import io

supabase_client: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

async def get_user_files_paths(user_id: str, job_id: str | None = None) -> dict[str, str]:
    """
    Retrieves all file paths of resumes for a given user and job from Supabase storage. The files not necessarily exist in the bucket.

    Args:
        user_id: The ID of the user
        job_id (optional): The ID of the job - if not provided, the job_id will be represented as "[job_id]"

    Returns:
        A dictionary of file paths containing "job_description_path", "tailored_resume_path", "original_resume_path", "recruiter_notes_path", "cover_letter_path"
    """
    if job_id is None:
        job_id = "[job_id]"

    response = {
        "user_full_resume_path": f"[bucket_name: temp]/{user_id}/FULL_RESUME.md",
        "job_description_path": f"[bucket_name: temp]/{user_id}/{job_id}/JOB_DESCRIPTION.md",
        "tailored_resume_path": f"[bucket_name: temp]/{user_id}/{job_id}/TAILORED_RESUME.md",
        "original_resume_path": f"[bucket_name: temp]/{user_id}/{job_id}/ORIGINAL_RESUME.md",
        "recruiter_notes_path": f"[bucket_name: temp]/{user_id}/{job_id}/NOTES.md",
        "cover_letter_path": f"[bucket_name: temp]/{user_id}/{job_id}/COVER_LETTER.md"
    }

    return response

async def read_file_from_bucket(bucket_name: str, file_path: str) -> Optional[bytes]:
    """
    Retrieves a file from a Supabase storage bucket.

    Args:
        bucket_name: The name of the bucket where the file is stored
        file_path: The path to the file within the bucket

    Returns:
        The file content as bytes if found, None otherwise
    """
    try:
        response = supabase_client.storage.from_(bucket_name).download(file_path)
        logging.debug(response)
        return response
    except Exception as e:
        print(f"Error retrieving file from bucket: {e}")
        return None

async def list_files_in_bucket(bucket_name: str, path: str = "") -> Optional[list]:
    """
    Lists all files in a given Supabase storage bucket (optionally within a folder/path).

    Args:
        bucket_name: The name of the bucket
        path: The folder/path within the bucket (default is root)

    Returns:
        A list of file details if successful, None otherwise
    """
    try:
        response = supabase_client.storage.from_(bucket_name).list(path)
        logging.debug(response)
        return response
    except Exception as e:
        print(f"Error listing files in bucket: {e}")
        return None

async def upload_file_to_bucket(bucket_name: str, file_path: str, file_content: str) -> Optional[dict]:
    """
    Uploads a file to a Supabase storage bucket, creating or overwriting as needed.

    Args:
        bucket_name: The name of the bucket
        file_path: The path (including filename) to upload to within the bucket
        file_content: The file content as string

    Returns:
        The upload response dict if successful, None otherwise
    """
    try:
        response = supabase_client.storage.from_(bucket_name).upload(
            file_path,
            file_content.encode("utf-8")
        )
        logging.debug(response)
        return response
    except Exception as e:
        print(f"Error uploading file to bucket: {e}")
        return None

async def delete_file_from_bucket(bucket_name: str, file_path: str) -> Optional[dict]:
    """
    Deletes a file from a Supabase storage bucket.

    Args:
        bucket_name: The name of the bucket
        file_path: The path to the file within the bucket

    Returns:
        The delete response dict if successful, None otherwise
    """
    try:
        response = supabase_client.storage.from_(bucket_name).remove([file_path])
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
