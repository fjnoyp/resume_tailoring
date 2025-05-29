"""
Info Collection Subgraph State

Conversational agent state for collecting missing resume information.
Updated to directly accept InterruptData from resume_tailorer.py
"""

from typing import TypedDict, Annotated, Optional, List, Dict, Any
from langgraph.graph.message import add_messages


class InfoCollectionState(TypedDict):
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
    missing_info: List[str]  # What we need to collect
    user_id: str  # User context
    full_resume: str  # Resume to update

    # Conversation management (required for react agent)
    messages: Annotated[List, add_messages]

    # Outputs
    final_collected_info: Optional[str] = None  # Formatted collected info
    updated_full_resume: Optional[str] = None  # Updated resume
    conversation_complete: bool = False  # Termination flag


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
    return {
        "missing_info": interrupt_data.get("missing_info", []),
        "user_id": interrupt_data.get("user_id", ""),
        "full_resume": interrupt_data.get("full_resume", ""),
        "messages": [],
        "final_collected_info": None,
        "updated_full_resume": None,
        "conversation_complete": False,
    }


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

    return {
        "missing_info": missing_info,
        "user_id": user_id,
        "full_resume": full_resume,
        "messages": [],
        "final_collected_info": None,
        "updated_full_resume": None,
        "conversation_complete": False,
    }
