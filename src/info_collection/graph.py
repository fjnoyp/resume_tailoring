"""
Info Collection Subgraph

Manages conversations with users to collect missing resume information.
"""

from langgraph.graph import StateGraph, START, END
from .state import InfoCollectionState
from .nodes import conversation_starter, question_asker, info_formatter, should_continue


def create_info_collection_graph() -> StateGraph:
    """
    Creates the info collection subgraph for user conversations.

    Flow:
    1. conversation_starter: Parse requirements and ask first question
    2. question_asker: Handle conversation flow and user responses
    3. info_formatter: Format collected information for main graph

    Uses conditional routing to manage conversation state.

    Returns:
        Compiled LangGraph for info collection
    """
    # Create subgraph with conversation state
    graph_builder = StateGraph(InfoCollectionState)

    # Add conversation nodes
    graph_builder.add_node("conversation_starter", conversation_starter)
    graph_builder.add_node("question_asker", question_asker)
    graph_builder.add_node("info_formatter", info_formatter)

    # Start with routing logic
    graph_builder.add_conditional_edges(
        START,
        should_continue,
        {
            "conversation_starter": "conversation_starter",
            "question_asker": "question_asker",
            "info_formatter": "info_formatter",
            "END": END,
        },
    )

    # Route from conversation_starter
    graph_builder.add_conditional_edges(
        "conversation_starter",
        should_continue,
        {
            "question_asker": "question_asker",
            "info_formatter": "info_formatter",
            "END": END,
        },
    )

    # Route from question_asker (main conversation loop)
    graph_builder.add_conditional_edges(
        "question_asker",
        should_continue,
        {
            "question_asker": "question_asker",
            "info_formatter": "info_formatter",
            "END": END,
        },
    )

    # Route from info_formatter
    graph_builder.add_edge("info_formatter", END)

    return graph_builder.compile()


# Create the info collection graph instance
info_collection_graph = create_info_collection_graph()
