"""
Info Collection Subgraph

Conversational agent flow for collecting missing resume information.
"""

from langgraph.graph import StateGraph, START, END
from .state import InfoCollectionState
from .nodes import (
    conversation_starter,
    conversation_agent,
    update_resume,
    should_continue,
)


def create_info_collection_graph() -> StateGraph:
    """
    Creates the conversational info collection subgraph.

    Flow:
    1. conversation_starter: Sets up context about missing info
    2. conversation_agent: React agent handles back-and-forth conversation
    3. update_resume: Formats collected info and updates full resume via update_user_profile

    Returns:
        Compiled LangGraph for info collection
    """
    # Create subgraph with conversational state
    graph_builder = StateGraph(InfoCollectionState)

    # Add nodes
    graph_builder.add_node("conversation_starter", conversation_starter)
    graph_builder.add_node("conversation_agent", conversation_agent)
    graph_builder.add_node("update_resume", update_resume)

    # Routing
    graph_builder.add_edge(START, "conversation_starter")

    graph_builder.add_conditional_edges(
        "conversation_starter",
        should_continue,
        {
            "conversation_agent": "conversation_agent",
            "update_resume": "update_resume",
        },
    )

    graph_builder.add_conditional_edges(
        "conversation_agent",
        should_continue,
        {
            "conversation_agent": "conversation_agent",
            "update_resume": "update_resume",
        },
    )

    graph_builder.add_edge("update_resume", END)

    return graph_builder.compile()


# Create the info collection graph instance
info_collection_graph = create_info_collection_graph()
