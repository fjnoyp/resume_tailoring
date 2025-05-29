"""
Main Resume Tailoring Graph

Clean, linear pipeline for resume tailoring with unified state management:
START → initialize_state → job_analyzer → resume_screener → resume_tailorer → END

Uses StateStorageManager for cohesive state loading/saving operations.
"""

import os
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.graphs.resume_rewrite.state import GraphState, set_error
from src.graphs.resume_rewrite.nodes import (
    job_analyzer,
    resume_screener,
    resume_tailorer,
)
from src.tools.state_storage_manager import load_resume_tailoring_data


async def initialize_state(state: GraphState, config) -> dict:
    """
    Initialize state by loading all required data using StateStorageManager.

    Replaces the old data_loader node with unified state management.
    """
    try:
        user_id = state["user_id"]
        job_id = state["job_id"]

        # Add metadata for tracing
        config["metadata"] = {
            **config.get("metadata", {}),
            "user_id": user_id,
            "job_id": job_id,
            "node": "initialize_state",
        }

        # Load all required data using StateStorageManager
        load_result = await load_resume_tailoring_data(user_id, job_id)

        if not load_result.success:
            return set_error(load_result.error)

        return load_result.loaded_fields

    except Exception as e:
        return set_error(f"State initialization failed: {str(e)}")


def create_graph() -> StateGraph:
    """
    Creates the main resume tailoring graph with unified state management.

    Pipeline:
    1. initialize_state: Load ALL files using StateStorageManager
    2. job_analyzer: Analyzes job to extract company strategy and requirements
    3. resume_screener: Evaluates resume from recruiter perspective
    4. resume_tailorer: Analyzes missing info and generates tailored resume

    Returns:
        Compiled LangGraph ready for execution with checkpointer for interrupts
    """
    # Create graph with simplified flat state
    graph_builder = StateGraph(GraphState)

    # Add processing nodes in pipeline order
    graph_builder.add_node("initialize_state", initialize_state)
    graph_builder.add_node("job_analyzer", job_analyzer)
    graph_builder.add_node("resume_screener", resume_screener)
    graph_builder.add_node("resume_tailorer", resume_tailorer)

    # Define linear pipeline
    graph_builder.add_edge(START, "initialize_state")
    graph_builder.add_edge("initialize_state", "job_analyzer")
    graph_builder.add_edge("job_analyzer", "resume_screener")
    graph_builder.add_edge("resume_screener", "resume_tailorer")
    graph_builder.add_edge("resume_tailorer", END)

    return graph_builder.compile()


# Create the main graph instance
graph = create_graph()
