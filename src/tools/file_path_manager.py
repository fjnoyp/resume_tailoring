"""
File Path Management

Centralized path management for all user and job-related files in storage.
Provides type safety and prevents magic string usage throughout the application.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class UserFilePaths:
    """
    Typed container for all user file paths in storage.
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

    def user_file_path(self, filename: str) -> str:
        """Path for any file in the user's root directory"""
        return f"{self.user_id}/{filename}"

    @property
    def user_directory_path(self) -> str:
        """Path to user's root directory"""
        return f"{self.user_id}/"

    @property
    def job_directory_path(self) -> str:
        """Path to specific job directory"""
        return f"{self.user_id}/{self.job_id}/"


def get_file_paths(user_id: str, job_id: Optional[str] = None) -> UserFilePaths:
    """
    Returns typed file paths for user and job.

    Args:
        user_id: Unique user identifier
        job_id: Unique job identifier (optional for user-only operations)

    Returns:
        UserFilePaths object with type-safe path properties
    """
    return UserFilePaths(user_id=user_id, job_id=job_id or "")


def get_field_to_path_mapping(file_paths: UserFilePaths) -> dict[str, str]:
    """
    Get mapping from state field names to file paths.

    Args:
        file_paths: UserFilePaths instance

    Returns:
        Dictionary mapping field names to file paths
    """
    return {
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
