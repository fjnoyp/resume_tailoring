"""
State-Aware Data Manager

Unified data persistence operations that understand state structure and provide high-level
operations for loading and saving state data across database tables and file storage. 
This is the ONLY public interface for state persistence operations - nodes should not 
access the database or storage directly.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, TypeVar
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timezone

from src.tools._supabase_storage_tools import (
    _read_file_from_bucket,
    _delete_file_from_bucket,
)

# Import Supabase client for database operations
from supabase import create_client, Client
import os

logging.basicConfig(level=logging.DEBUG)

# Type variables for state types
StateType = TypeVar("StateType", bound=Dict[str, Any])

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # This bypasses RLS

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY environment variables")

# Use service role for AI operations - bypasses RLS policies  
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


class StateLoadMode(Enum):
    """Defines what data to load for different graph types"""

    RESUME_TAILORING = "resume_tailoring"  # Load job + resume data
    USER_PROFILE_UPDATE = "user_profile_update"  # Load user resume only
    COVER_LETTER = "cover_letter"  # Load job + resume + feedback data


@dataclass
class StateLoadResult:
    """Result of state loading operation"""

    success: bool
    loaded_fields: Dict[str, Any]
    missing_fields: list[str]
    error: Optional[str] = None


@dataclass
class FileInfo:
    """Information about a file in storage"""

    name: str
    path: str
    size: Optional[int] = None
    last_modified: Optional[str] = None


class StateDataManager:
    """
    Unified data persistence manager that understands state structure and provides
    high-level operations for loading and saving state data across database tables
    and file storage.

    This is the ONLY public interface for state persistence operations.
    """

    @staticmethod
    async def load_state_data(
        user_id: str,
        job_id: Optional[str] = None,
        mode: StateLoadMode = StateLoadMode.RESUME_TAILORING,
    ) -> StateLoadResult:
        """
        Load state data based on the specified mode.

        Args:
            user_id: User identifier
            job_id: Job identifier (optional for user-only operations)
            mode: What type of data to load

        Returns:
            StateLoadResult with loaded data and status
        """
        try:
            loaded_fields = {}
            missing_fields = []

            # Load user data if needed
            if mode in [StateLoadMode.RESUME_TAILORING, StateLoadMode.USER_PROFILE_UPDATE, StateLoadMode.COVER_LETTER]:
                user_data = await StateDataManager._load_user_data(user_id)
                if user_data:
                    if mode == StateLoadMode.USER_PROFILE_UPDATE:
                        loaded_fields["current_full_resume"] = user_data.get("full_resume", "")
                    else:
                        loaded_fields["original_resume"] = user_data.get("original_resume", "")
                        loaded_fields["full_resume"] = user_data.get("full_resume", "")
                else:
                    if mode == StateLoadMode.USER_PROFILE_UPDATE:
                        loaded_fields["current_full_resume"] = ""
                    else:
                        missing_fields.append("user data")

            # Load job data if needed
            if job_id and mode in [StateLoadMode.RESUME_TAILORING, StateLoadMode.COVER_LETTER]:
                job_data = await StateDataManager._load_job_data(job_id)
                if job_data:
                    loaded_fields["job_description"] = job_data.get("job_description", "")
                    
                    if mode == StateLoadMode.RESUME_TAILORING:
                        # Optional fields for resume tailoring
                        loaded_fields["company_strategy"] = job_data.get("company_strategy", "")
                        loaded_fields["tailored_resume"] = job_data.get("tailored_resume", "")
                        loaded_fields["tailored_cv"] = job_data.get("tailored_cv", "")
                        
                    elif mode == StateLoadMode.COVER_LETTER:
                        # Required fields for cover letter
                        tailored_resume = job_data.get("tailored_resume", "")
                        recruiter_feedback = job_data.get("recruiter_feedback", "")
                        
                        if not tailored_resume:
                            missing_fields.append("tailored_resume")
                        if not recruiter_feedback:
                            missing_fields.append("recruiter_feedback")
                            
                        loaded_fields["tailored_resume"] = tailored_resume
                        loaded_fields["recruiter_feedback"] = recruiter_feedback
                        loaded_fields["company_strategy"] = job_data.get("company_strategy", "")
                else:
                    missing_fields.append("job data")

            # Check if we have all required data
            if missing_fields:
                return StateLoadResult(
                    success=False,
                    loaded_fields=loaded_fields,
                    missing_fields=missing_fields,
                    error=f"Missing required data: {', '.join(missing_fields)}",
                )

            logging.debug(
                f"[StateData] Successfully loaded {len(loaded_fields)} fields for {mode.value}"
            )
            return StateLoadResult(
                success=True, loaded_fields=loaded_fields, missing_fields=[]
            )

        except Exception as e:
            logging.error(f"[StateData] Error loading state data: {e}")
            return StateLoadResult(
                success=False,
                loaded_fields={},
                missing_fields=[],
                error=f"State loading failed: {str(e)}",
            )

    @staticmethod
    async def save_state_field(
        user_id: str, job_id: Optional[str], field_name: str, content: str
    ) -> bool:
        """
        Save a single state field to the database.

        Args:
            user_id: User identifier
            job_id: Job identifier (optional)
            field_name: Name of the state field
            content: Content to save

        Returns:
            True if successful, False otherwise
        """
        try:
            # Map field names to table operations
            user_fields = ["full_resume", "original_resume"]
            job_fields = ["job_description", "company_strategy", "recruiter_feedback", 
                         "tailored_resume", "tailored_cv", "confidence_score", "status", 
                         "job_title", "company_name"]

            if field_name in user_fields:
                return await StateDataManager._save_user_field(user_id, field_name, content)
            elif field_name in job_fields and job_id:
                return await StateDataManager._save_job_field(job_id, field_name, content)
            else:
                logging.error(f"[StateData] Unknown field name or missing job_id: {field_name}")
                return False

        except Exception as e:
            logging.error(f"[StateData] Error saving {field_name}: {e}")
            return False

    @staticmethod
    async def save_multiple_fields(
        user_id: str, job_id: Optional[str], fields: Dict[str, str]
    ) -> Dict[str, bool]:
        """
        Save multiple state fields to the database.

        Args:
            user_id: User identifier
            job_id: Job identifier (optional)
            fields: Dictionary of field_name -> content

        Returns:
            Dictionary of field_name -> success_status
        """
        results = {}
        for field_name, content in fields.items():
            results[field_name] = await StateDataManager.save_state_field(
                user_id, job_id, field_name, content
            )
        return results

    @staticmethod
    async def read_temp_file(
        user_id: str, filename: str
    ) -> Optional[str]:
        """
        Read a temp file from the user-files storage bucket.

        Args:
            user_id: User identifier
            filename: Name of the file to read

        Returns:
            File content as string, or None if not found
        """
        try:
            file_path = f"{user_id}/temp/{filename}"
            file_bytes = await _read_file_from_bucket(file_path)
            
            if file_bytes:
                return file_bytes.decode("utf-8")
            return None

        except Exception as e:
            logging.error(f"[StateData] Error reading file {filename}: {e}")
            return None

    @staticmethod
    async def read_temp_file_bytes(
        user_id: str, filename: str
    ) -> Optional[bytes]:
        """
        Read a temp file as bytes from the user-files storage bucket.

        Args:
            user_id: User identifier
            filename: Name of the file to read

        Returns:
            File content as bytes, or None if not found
        """
        try:
            file_path = f"{user_id}/temp/{filename}"
            logging.debug(f"[StateData] Attempting to read file: {file_path}")
            
            file_bytes = await _read_file_from_bucket(file_path)
            
            if file_bytes:
                logging.debug(f"[StateData] Successfully read file: {file_path}, size: {len(file_bytes)} bytes")
                return file_bytes
            else:
                logging.error(f"[StateData] File read returned None/empty: {file_path}")
                return None

        except Exception as e:
            logging.error(f"[StateData] Error reading file bytes {filename}: {e}")
            logging.error(f"[StateData] Full path attempted: {user_id}/temp/{filename}")
            return None

    @staticmethod
    async def delete_temp_file(
        user_id: str, filename: str
    ) -> bool:
        """
        Delete a temp file from user directory.

        Args:
            user_id: User identifier
            filename: Name of the file to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = f"{user_id}/temp/{filename}"
            result = await _delete_file_from_bucket(file_path)
            
            if result:
                logging.debug(f"[StateData] Deleted file: {file_path}")
                return True
            else:
                logging.error(f"[StateData] Failed to delete file: {filename}")
                return False

        except Exception as e:
            logging.error(f"[StateData] Error deleting file {filename}: {e}")
            return False

    @staticmethod
    async def save_chat_message(
        job_id: str,
        content: str,
        role: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save a chat message to the chat_messages table.

        Args:
            job_id: Job identifier
            content: Message content
            role: Message role ('user', 'ai', 'system', 'tool')
            metadata: Optional metadata as JSON object

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate role
            valid_roles = ['user', 'ai', 'system', 'tool']
            if role not in valid_roles:
                logging.error(f"[StateData] Invalid role: {role}. Must be one of {valid_roles}")
                return False

            def _sync_save_message():
                insert_data = {
                    "job_id": job_id,
                    "content": content,
                    "role": role
                }
                
                if metadata:
                    insert_data["metadata"] = metadata
                
                result = supabase.table("chat_messages").insert(insert_data).execute()
                return result.data is not None and len(result.data) > 0
            
            # Wrap synchronous Supabase call in asyncio.to_thread to avoid blocking
            success = await asyncio.to_thread(_sync_save_message)
            
            if success:
                logging.debug(f"[StateData] Saved chat message for job {job_id}: {role} - {len(content)} chars")
                return True
            else:
                logging.error(f"[StateData] Failed to save chat message for job {job_id}")
                return False

        except Exception as e:
            logging.error(f"[StateData] Error saving chat message: {e}")
            return False

    # Private helper methods for database operations

    @staticmethod
    async def _load_user_data(user_id: str) -> Optional[Dict[str, Any]]:
        """Load user data from the database."""
        try:
            # Wrap synchronous Supabase call in asyncio.to_thread to avoid blocking
            def _sync_load_user():
                result = supabase.table("users").select("*").eq("id", user_id).execute()
                return result.data[0] if result.data else None
            
            return await asyncio.to_thread(_sync_load_user)
        except Exception as e:
            logging.error(f"[StateData] Error loading user data: {e}")
            return None

    @staticmethod
    async def _load_job_data(job_id: str) -> Optional[Dict[str, Any]]:
        """Load job data from the database."""
        try:
            # Wrap synchronous Supabase call in asyncio.to_thread to avoid blocking
            def _sync_load_job():
                result = supabase.table("jobs").select("*").eq("id", job_id).execute()
                return result.data[0] if result.data else None
            
            return await asyncio.to_thread(_sync_load_job)
        except Exception as e:
            logging.error(f"[StateData] Error loading job data: {e}")
            return None

    @staticmethod
    async def _save_user_field(user_id: str, field_name: str, content: str) -> bool:
        """Save a field to the users table."""
        try:
            def _sync_save_user():
                update_data = {
                    field_name: content,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                
                result = supabase.table("users").update(update_data).eq("id", user_id).execute()
                return result.data is not None
            
            # Wrap synchronous Supabase call in asyncio.to_thread to avoid blocking
            success = await asyncio.to_thread(_sync_save_user)
            
            if success:
                logging.debug(f"[StateData] Updated user {field_name}: {len(content)} chars")
                return True
            else:
                logging.error(f"[StateData] Failed to update user {field_name}")
                return False

        except Exception as e:
            logging.error(f"[StateData] Error saving user field {field_name}: {e}")
            return False

    @staticmethod
    async def _save_job_field(job_id: str, field_name: str, content: str) -> bool:
        """Save a field to the jobs table."""
        try:
            def _sync_save_job():
                update_data = {
                    field_name: content,
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                
                result = supabase.table("jobs").update(update_data).eq("id", job_id).execute()
                return result.data is not None
            
            # Wrap synchronous Supabase call in asyncio.to_thread to avoid blocking
            success = await asyncio.to_thread(_sync_save_job)
            
            if success:
                logging.debug(f"[StateData] Updated job {field_name}: {len(content)} chars")
                return True
            else:
                logging.error(f"[StateData] Failed to update job {field_name}")
                return False

        except Exception as e:
            logging.error(f"[StateData] Error saving job field {field_name}: {e}")
            return False


# Convenience functions for common operations
async def load_resume_tailoring_data(user_id: str, job_id: str) -> StateLoadResult:
    """Load data for resume tailoring pipeline."""
    return await StateDataManager.load_state_data(
        user_id, job_id, StateLoadMode.RESUME_TAILORING
    )


async def load_user_profile_data(user_id: str) -> StateLoadResult:
    """Load data for user profile updates."""
    return await StateDataManager.load_state_data(
        user_id, None, StateLoadMode.USER_PROFILE_UPDATE
    )


async def save_processing_result(
    user_id: str, job_id: Optional[str], field_name: str, content: str
) -> bool:
    """Save a processing result to the database."""
    return await StateDataManager.save_state_field(
        user_id, job_id, field_name, content
    )
