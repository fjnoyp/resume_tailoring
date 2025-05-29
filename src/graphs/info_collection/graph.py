"""
Info Collection Subgraph

Conversational agent flow for collecting missing resume information.
"""

from langgraph.graph import StateGraph, START, END
from .state import InfoCollectionState
from .nodes import (
    info_collector_agent,
    update_resume_with_collected_info,
)


def should_continue(state: InfoCollectionState) -> str:
    """
    Routing function to determine if conversation should continue or terminate.

    Args:
        state: Current conversation state

    Returns:
        Next node name
    """
    # Check if conversation should terminate
    if state.conversation_complete:
        return "update_resume_with_collected_info"

    # Continue conversation
    return "info_collector_agent"


def create_info_collection_graph() -> StateGraph:
    """
    Creates the conversational info collection subgraph.

    Flow:
    1. info_collector_agent: Handles conversation and collects missing info
    2. update_resume_with_collected_info: Updates full resume with collected information

    Returns:
        Compiled LangGraph for info collection
    """
    # Create subgraph with conversational state
    graph_builder = StateGraph(InfoCollectionState)

    # Add nodes
    graph_builder.add_node("info_collector_agent", info_collector_agent)
    graph_builder.add_node(
        "update_resume_with_collected_info", update_resume_with_collected_info
    )

    # Routing
    graph_builder.add_edge(START, "info_collector_agent")

    graph_builder.add_conditional_edges(
        "info_collector_agent",
        should_continue,
        {
            "info_collector_agent": END, # We route to end to prevent infinite loops and properly wait for the user to respond
            "update_resume_with_collected_info": "update_resume_with_collected_info",
        },
    )

    graph_builder.add_edge("update_resume_with_collected_info", END)

    return graph_builder.compile()


# Create the info collection graph instance
info_collection_graph = create_info_collection_graph()
