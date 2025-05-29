from typing import TypedDict, Optional


class UpdateUserProfileState(TypedDict):
    """
    Simplified flat state for user profile updates with clear field ownership.

    CONTEXT (Immutable):
        graph_type: Identifies this as "update_user_profile" state
        user_id: Session user identifier

    CONTROL FLOW:
        operation_mode: Determines which processing path to take
            - "update_resume": Direct resume update from new information
            - "parse_linkedin": Parse LinkedIn profile and merge into resume
            - "parse_file": Parse additional file and merge into resume

    INPUT DATA (Loaded by data_loader or provided by caller):
        input_data: Raw input content to process (LinkedIn profile, file content, or direct info)
        current_full_resume: User's existing full resume content

    PROCESSING OUTPUTS:
        updated_full_resume: Updated resume content after processing
        parsed_content: Intermediate parsed content (for LinkedIn/file processing)

    ERROR HANDLING:
        error: Error message if processing fails
    """

    # Context (set once, never changes)
    user_id: str

    # Control flow
    operation_mode: str  # "update_resume", "parse_linkedin", "parse_file"

    # Input data
    input_data: str
    current_full_resume: Optional[str] = None

    # Processing outputs
    updated_full_resume: Optional[str] = None
    parsed_content: Optional[str] = None

    # Error handling
    error: Optional[str] = None


def create_update_profile_state(
    user_id: str, operation_mode: str, input_data: str
) -> UpdateUserProfileState:
    """Create initial state for user profile update"""
    return {
        "user_id": user_id,
        "operation_mode": operation_mode,
        "input_data": input_data,
        "current_full_resume": None,
        "updated_full_resume": None,
        "parsed_content": None,
        "error": None,
    }


def set_error(error_msg: str) -> dict:
    """Helper for setting error state"""
    return {"error": error_msg}
