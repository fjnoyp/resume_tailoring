import os
from typing import Optional
from supabase import create_client, Client

supabase_client: Client = create_client(os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_KEY"))

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
        return response
    except Exception as e:
        print(f"Error listing files in bucket: {e}")
        return None

async def upload_file_to_bucket(bucket_name: str, file_path: str, file_content: bytes) -> Optional[dict]:
    """
    Uploads a file to a Supabase storage bucket.

    Args:
        bucket_name: The name of the bucket
        file_path: The path (including filename) to upload to within the bucket
        file_content: The file content as bytes

    Returns:
        The upload response dict if successful, None otherwise
    """
    try:
        response = supabase_client.storage.from_(bucket_name).upload(file_path, file_content)
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
