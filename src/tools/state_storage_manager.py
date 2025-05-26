"""
State-Aware Storage Manager

Unified storage operations that understand state structure and provide high-level
operations for loading and saving state data. Eliminates redundant data loaders
and provides cohesive view of state management.
"""

import logging
from typing import Dict, Any, Optional, TypeVar, Union
from dataclasses import dataclass
from enum import Enum

from src.tools.supabase_storage_tools import (
    get_file_paths,
    read_file_from_bucket,
    upload_file_to_bucket,
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


class StateStorageManager:
    """
    Unified storage manager that understands state structure and provides
    high-level operations for loading and saving state data.
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
            file_paths = get_file_paths(user_id, job_id or "")
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
            file_paths = get_file_paths(user_id, job_id or "")
            file_path = StateStorageManager._get_file_path_for_field(
                field_name, file_paths
            )

            if not file_path:
                logging.error(f"[StateStorage] Unknown field name: {field_name}")
                return False

            result = await upload_file_to_bucket(file_path, content)
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
    def _get_file_specs_for_mode(
        mode: StateLoadMode, file_paths
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
    def _get_file_path_for_field(field_name: str, file_paths) -> Optional[str]:
        """Get the file path for a given state field name."""
        field_to_path = {
            "job_description": file_paths.job_description_path,
            "original_resume": file_paths.original_resume_path,
            "full_resume": file_paths.user_full_resume_path,
            "current_full_resume": file_paths.user_full_resume_path,
            "job_strategy": file_paths.job_strategy_path,
            "recruiter_feedback": file_paths.recruiter_feedback_path,
            "tailored_resume": file_paths.tailored_resume_path,
            "cover_letter": file_paths.cover_letter_path,
            "updated_full_resume": file_paths.user_full_resume_path,
        }
        return field_to_path.get(field_name)

    @staticmethod
    async def _load_file_content(file_path: str) -> Optional[str]:
        """Load and decode file content from storage."""
        try:
            file_bytes = await read_file_from_bucket(file_path)
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
