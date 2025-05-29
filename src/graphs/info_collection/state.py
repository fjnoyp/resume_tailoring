"""
Info Collection Subgraph State

Conversational agent state for collecting missing resume information.
Updated to directly accept InterruptData from resume_tailorer.py
"""

from typing import Annotated, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from langgraph.graph.message import add_messages


class InfoCollectionState(BaseModel):
    """
    State for conversational info collection subgraph.

    INPUTS:
        missing_info: List of specific missing information to collect
        user_id: User identifier for context
        full_resume: Current full resume content for updating

    CONVERSATION:
        messages: Conversation history with user (required for react agent)

    OUTPUTS:
        final_collected_info: All information collected from user (formatted)
        updated_full_resume: Updated full resume content after incorporating new info
        conversation_complete: Flag indicating conversation should terminate
    """

    # Essential inputs
    missing_info: List[str] = Field(..., description="What we need to collect")
    user_id: str = Field(..., description="User context")
    full_resume: str = Field(..., description="Resume to update")

    # Conversation management (required for react agent)
    messages: Annotated[List, add_messages] = Field(
        default_factory=list, description="Conversation history"
    )

    # Outputs
    final_collected_info: Optional[str] = Field(
        None, description="Formatted collected info"
    )
    updated_full_resume: Optional[str] = Field(None, description="Updated resume")
    conversation_complete: bool = Field(False, description="Termination flag")


def create_info_collection_state_from_interrupt(
    interrupt_data: Dict[str, Any],
) -> InfoCollectionState:
    """
    Create info collection state directly from InterruptData payload.

    Args:
        interrupt_data: Dictionary containing InterruptData from resume_tailorer interrupt

    Returns:
        InfoCollectionState ready for processing
    """
    return InfoCollectionState(
        missing_info=interrupt_data.get("missing_info", []),
        user_id=interrupt_data.get("user_id", ""),
        full_resume=interrupt_data.get("full_resume", ""),
    )


def create_info_collection_state(
    missing_info_requirements: str, user_id: str, full_resume: str = ""
) -> InfoCollectionState:
    """
    Legacy function for backward compatibility.

    Args:
        missing_info_requirements: JSON string with missing info analysis
        user_id: User identifier
        full_resume: Current full resume content

    Returns:
        InfoCollectionState ready for processing
    """
    # Parse the requirements if it's a JSON string
    import json

    try:
        requirements_data = json.loads(missing_info_requirements)
        missing_info = requirements_data.get("missing_info", [])
    except (json.JSONDecodeError, TypeError):
        # Fallback to treating it as a simple list
        missing_info = [missing_info_requirements] if missing_info_requirements else []

    return InfoCollectionState(
        missing_info=missing_info,
        user_id=user_id,
        full_resume=full_resume,
    )
