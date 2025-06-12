from typing import Optional
from pydantic import BaseModel, Field


class CoverLetterState(BaseModel):
    """
    State for cover letter generation and evaluation workflow.

    CONTEXT (Immutable):
        user_id: Session user identifier
        job_id: Session job identifier

    INPUT DATA (Required):
        job_description: Raw job posting text
        tailored_resume: Customized resume for the job
        recruiter_feedback: Resume evaluation from recruiter perspective
        full_resume: User's complete resume with all details

    PROCESSING OUTPUTS:
        cover_letter: Generated cover letter content

    ERROR HANDLING:
        error: Error message if processing fails
    """

    # Context (set once, never changes)
    user_id: str = Field(..., description="Session user identifier")
    job_id: str = Field(..., description="Session job identifier")

    # Input data (loaded from database/storage)
    job_description: Optional[str] = Field(None, description="Raw job posting text")
    tailored_resume: Optional[str] = Field(
        None, description="Customized resume for the job"
    )
    recruiter_feedback: Optional[str] = Field(
        None, description="Resume evaluation from recruiter perspective"
    )
    full_resume: Optional[str] = Field(
        None, description="User's complete resume with all details"
    )

    # Processing outputs
    cover_letter: Optional[str] = Field(
        None, description="Generated cover letter content"
    )

    # Error handling
    error: Optional[str] = Field(None, description="Error message if processing fails")


def create_cover_letter_state(user_id: str, job_id: str) -> CoverLetterState:
    """Create initial cover letter state with required context"""
    return CoverLetterState(
        user_id=user_id,
        job_id=job_id,
    )


def set_error(error_msg: str) -> dict:
    """Helper for setting error state"""
    return {"error": error_msg} 