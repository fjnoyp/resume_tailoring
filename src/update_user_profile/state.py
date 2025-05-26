from enum import Enum
from typing import TypedDict, Optional

class AiBehaviorMode(Enum):
    UPDATE_USER_FULL_RESUME = "update_user_full_resume"
    PARSE_LINKEDIN_PROFILE = "parse_linkedin_profile"
    PARSE_ADDITIONAL_FILE = "parse_additional_file"

class FullResumeGraphState(TypedDict):
    """
    State for the full resume update graph.
    """

    # Context (set once, never changes)
    user_id: str

    ai_behavior_mode: str = AiBehaviorMode.UPDATE_USER_FULL_RESUME.value

    full_resume: Optional[str] = None

    # Input data (depends on ai_behavior_mode)
    input_data: str