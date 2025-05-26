"""
State-Aware Storage Manager

Unified storage operations that understand state structure and provide high-level
operations for loading and saving state data. This is the ONLY public interface
for storage operations - nodes should not access storage directly.
"""

import logging
from typing import Dict, Any, Optional, TypeVar, Union, List
from dataclasses import dataclass
from enum import Enum

from src.tools._supabase_storage_tools import (
    _read_file_from_bucket,
    _upload_file_to_bucket,
    _list_files_in_bucket,
    _delete_file_from_bucket,
)
from src.tools.file_path_manager import (
    get_file_paths,
    get_field_to_path_mapping,
    UserFilePaths,
)

logging.basicConfig(level=logging.DEBUG)

# Type variables for state types
StateType = TypeVar("StateType", bound=Dict[str, Any])


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
    missing_files: list[str]
    error: Optional[str] = None


@dataclass
class FileInfo:
    """Information about a file in storage"""

    name: str
    path: str
    size: Optional[int] = None
    last_modified: Optional[str] = None


class StateStorageManager:
    """
    Unified storage manager that understands state structure and provides
    high-level operations for loading and saving state data.

    This is the ONLY public interface for storage operations.
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
            file_paths = get_file_paths(user_id, job_id)
            loaded_fields = {}
            missing_files = []

            # Define what files to load for each mode
            file_specs = StateStorageManager._get_file_specs_for_mode(mode, file_paths)

            # Load each required file
            for field_name, file_path, required in file_specs:
                content = await StateStorageManager._load_file_content(file_path)

                if content is not None:
                    loaded_fields[field_name] = content
                    logging.debug(
                        f"[StateStorage] Loaded {field_name}: {len(content)} chars"
                    )
                else:
                    if required:
                        missing_files.append(f"{field_name} ({file_path})")
                    else:
                        loaded_fields[field_name] = (
                            ""  # Optional files default to empty
                        )
                        logging.debug(
                            f"[StateStorage] Optional file not found: {field_name}"
                        )

            # Check if we have all required files
            if missing_files:
                return StateLoadResult(
                    success=False,
                    loaded_fields=loaded_fields,
                    missing_files=missing_files,
                    error=f"Missing required files: {', '.join(missing_files)}",
                )

            logging.debug(
                f"[StateStorage] Successfully loaded {len(loaded_fields)} fields for {mode.value}"
            )
            return StateLoadResult(
                success=True, loaded_fields=loaded_fields, missing_files=[]
            )

        except Exception as e:
            logging.error(f"[StateStorage] Error loading state data: {e}")
            return StateLoadResult(
                success=False,
                loaded_fields={},
                missing_files=[],
                error=f"State loading failed: {str(e)}",
            )

    @staticmethod
    async def save_state_field(
        user_id: str, job_id: Optional[str], field_name: str, content: str
    ) -> bool:
        """
        Save a single state field to storage.

        Args:
            user_id: User identifier
            job_id: Job identifier (optional)
            field_name: Name of the state field
            content: Content to save

        Returns:
            True if successful, False otherwise
        """
        try:
            file_paths = get_file_paths(user_id, job_id)
            field_to_path = get_field_to_path_mapping(file_paths)
            file_path = field_to_path.get(field_name)

            if not file_path:
                logging.error(f"[StateStorage] Unknown field name: {field_name}")
                return False

            result = await _upload_file_to_bucket(file_path, content)
            if result:
                logging.debug(
                    f"[StateStorage] Saved {field_name}: {len(content)} chars to {file_path}"
                )
                return True
            else:
                logging.error(f"[StateStorage] Failed to save {field_name}")
                return False

        except Exception as e:
            logging.error(f"[StateStorage] Error saving {field_name}: {e}")
            return False

    @staticmethod
    async def save_multiple_fields(
        user_id: str, job_id: Optional[str], fields: Dict[str, str]
    ) -> Dict[str, bool]:
        """
        Save multiple state fields to storage.

        Args:
            user_id: User identifier
            job_id: Job identifier (optional)
            fields: Dictionary of field_name -> content

        Returns:
            Dictionary of field_name -> success_status
        """
        results = {}
        for field_name, content in fields.items():
            results[field_name] = await StateStorageManager.save_state_field(
                user_id, job_id, field_name, content
            )
        return results

    @staticmethod
    async def read_file(
        user_id: str, filename: str, job_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Read a custom file from user or job directory.

        Args:
            user_id: User identifier
            filename: Name of the file to read
            job_id: Job identifier (if file is in job directory)

        Returns:
            File content as string, or None if not found
        """
        try:
            file_paths = get_file_paths(user_id, job_id)

            if job_id:
                file_path = file_paths.custom_file_path(filename)
            else:
                file_path = file_paths.user_file_path(filename)

            return await StateStorageManager._load_file_content(file_path)

        except Exception as e:
            logging.error(f"[StateStorage] Error reading file {filename}: {e}")
            return None

    @staticmethod
    async def read_file_bytes(
        user_id: str, filename: str, job_id: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Read a custom file as bytes from user or job directory.

        Args:
            user_id: User identifier
            filename: Name of the file to read
            job_id: Job identifier (if file is in job directory)

        Returns:
            File content as bytes, or None if not found
        """
        try:
            file_paths = get_file_paths(user_id, job_id)

            if job_id:
                file_path = file_paths.custom_file_path(filename)
            else:
                file_path = file_paths.user_file_path(filename)

            return await _read_file_from_bucket(file_path)

        except Exception as e:
            logging.error(f"[StateStorage] Error reading file bytes {filename}: {e}")
            return None

    @staticmethod
    async def save_file(
        user_id: str, filename: str, content: str, job_id: Optional[str] = None
    ) -> bool:
        """
        Save a custom file to user or job directory.

        Args:
            user_id: User identifier
            filename: Name of the file to save
            content: File content
            job_id: Job identifier (if file should be in job directory)

        Returns:
            True if successful, False otherwise
        """
        try:
            file_paths = get_file_paths(user_id, job_id)

            if job_id:
                file_path = file_paths.custom_file_path(filename)
            else:
                file_path = file_paths.user_file_path(filename)

            result = await _upload_file_to_bucket(file_path, content)
            if result:
                logging.debug(f"[StateStorage] Saved custom file: {file_path}")
                return True
            else:
                logging.error(f"[StateStorage] Failed to save custom file: {filename}")
                return False

        except Exception as e:
            logging.error(f"[StateStorage] Error saving file {filename}: {e}")
            return False

    @staticmethod
    async def list_files(user_id: str, job_id: Optional[str] = None) -> List[FileInfo]:
        """
        List files in user or job directory.

        Args:
            user_id: User identifier
            job_id: Job identifier (optional, lists job directory if provided)

        Returns:
            List of FileInfo objects
        """
        try:
            file_paths = get_file_paths(user_id, job_id)

            if job_id:
                directory_path = file_paths.job_directory_path
            else:
                directory_path = file_paths.user_directory_path

            files_data = await _list_files_in_bucket(directory_path)

            if not files_data:
                return []

            file_infos = []
            for file_data in files_data:
                if isinstance(file_data, dict) and file_data.get("name"):
                    file_info = FileInfo(
                        name=file_data["name"],
                        path=f"{directory_path}{file_data['name']}",
                        size=file_data.get("metadata", {}).get("size"),
                        last_modified=file_data.get("updated_at"),
                    )
                    file_infos.append(file_info)

            return file_infos

        except Exception as e:
            logging.error(f"[StateStorage] Error listing files: {e}")
            return []

    @staticmethod
    async def delete_file(
        user_id: str, filename: str, job_id: Optional[str] = None
    ) -> bool:
        """
        Delete a file from user or job directory.

        Args:
            user_id: User identifier
            filename: Name of the file to delete
            job_id: Job identifier (if file is in job directory)

        Returns:
            True if successful, False otherwise
        """
        try:
            file_paths = get_file_paths(user_id, job_id)

            if job_id:
                file_path = file_paths.custom_file_path(filename)
            else:
                file_path = file_paths.user_file_path(filename)

            result = await _delete_file_from_bucket(file_path)
            if result:
                logging.debug(f"[StateStorage] Deleted file: {file_path}")
                return True
            else:
                logging.error(f"[StateStorage] Failed to delete file: {filename}")
                return False

        except Exception as e:
            logging.error(f"[StateStorage] Error deleting file {filename}: {e}")
            return False

    @staticmethod
    def _get_file_specs_for_mode(
        mode: StateLoadMode, file_paths: UserFilePaths
    ) -> list[tuple[str, str, bool]]:
        """
        Get file specifications (field_name, file_path, required) for a given mode.

        Returns:
            List of (field_name, file_path, is_required) tuples
        """
        if mode == StateLoadMode.RESUME_TAILORING:
            return [
                ("job_description", file_paths.job_description_path, True),
                ("original_resume", file_paths.original_resume_path, True),
                ("full_resume", file_paths.user_full_resume_path, False),
            ]
        elif mode == StateLoadMode.USER_PROFILE_UPDATE:
            return [
                ("current_full_resume", file_paths.user_full_resume_path, False),
            ]
        elif mode == StateLoadMode.COVER_LETTER:
            return [
                ("job_description", file_paths.job_description_path, True),
                ("tailored_resume", file_paths.tailored_resume_path, True),
                ("recruiter_feedback", file_paths.recruiter_feedback_path, True),
                ("full_resume", file_paths.user_full_resume_path, False),
            ]
        else:
            return []

    @staticmethod
    async def _load_file_content(file_path: str) -> Optional[str]:
        """Load and decode file content from storage."""
        try:
            file_bytes = await _read_file_from_bucket(file_path)
            if file_bytes:
                return file_bytes.decode("utf-8")
            return None
        except Exception as e:
            logging.error(f"[StateStorage] Error loading file {file_path}: {e}")
            return None


# Convenience functions for common operations
async def load_resume_tailoring_data(user_id: str, job_id: str) -> StateLoadResult:
    """Load data for resume tailoring pipeline."""
    return await StateStorageManager.load_state_data(
        user_id, job_id, StateLoadMode.RESUME_TAILORING
    )


async def load_user_profile_data(user_id: str) -> StateLoadResult:
    """Load data for user profile updates."""
    return await StateStorageManager.load_state_data(
        user_id, None, StateLoadMode.USER_PROFILE_UPDATE
    )


async def save_processing_result(
    user_id: str, job_id: Optional[str], field_name: str, content: str
) -> bool:
    """Save a processing result to storage."""
    return await StateStorageManager.save_state_field(
        user_id, job_id, field_name, content
    )
