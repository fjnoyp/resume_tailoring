"""
Info Collection Subgraph State

Manages conversation state for collecting missing resume information from users.
"""

from typing import TypedDict, Annotated, Optional, List, Dict, Any
from langgraph.graph.message import add_messages


class InfoCollectionState(TypedDict):
    """
    State for info collection subgraph focused on user conversations.

    INPUT (from main graph):
        missing_info_requirements: What information needs to be collected
        user_id: Session user identifier

    CONVERSATION MANAGEMENT:
        messages: Conversation history with user
        collected_info: Information gathered so far
        remaining_questions: Questions still to ask

    OUTPUT (back to main graph):
        final_collected_info: All information collected from user

    CONTROL:
        is_complete: Whether collection is finished
        error: Error message if collection fails
    """

    # Input from main graph
    missing_info_requirements: str  # JSON string with missing info analysis
    user_id: str

    # Conversation management
    messages: Annotated[List, add_messages]
    collected_info: Dict[str, Any]  # Structured collected information
    remaining_questions: List[str]  # Questions still to ask

    # Output to main graph
    final_collected_info: Optional[str] = None  # Formatted final result

    # Control
    is_complete: bool = False
    error: Optional[str] = None


def create_info_collection_state(
    missing_info_requirements: str, user_id: str
) -> InfoCollectionState:
    """Create initial state for info collection subgraph"""
    return {
        "missing_info_requirements": missing_info_requirements,
        "user_id": user_id,
        "messages": [],
        "collected_info": {},
        "remaining_questions": [],
        "final_collected_info": None,
        "is_complete": False,
        "error": None,
    }
