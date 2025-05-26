"""
User Profile Update Graph

Handles different ways to update a user's full resume:
1. Direct update from new information
2. Parse LinkedIn profile and merge
3. Parse additional files and merge

Uses StateStorageManager for unified state management.
"""

from langgraph.graph import StateGraph, START, END
from src.update_user_profile.nodes.update_user_full_resume import resume_updater
from src.update_user_profile.nodes.parse_linkedin_profile import linkedin_parser
from src.update_user_profile.nodes.parse_file_to_markdown import file_parser
from src.update_user_profile.state import UpdateUserProfileState, set_error
from src.tools.state_storage_manager import load_user_profile_data


async def initialize_profile_state(state: UpdateUserProfileState, config) -> dict:
    """
    Initialize state by loading user profile data using StateStorageManager.

    Replaces the old data_loader node with unified state management.
    """
    try:
        user_id = state["user_id"]

        # Add metadata for tracing
        config["metadata"] = {
            **config.get("metadata", {}),
            "user_id": user_id,
            "node": "initialize_profile_state",
            "graph": "update_user_profile",
        }

        # Load user profile data using StateStorageManager
        load_result = await load_user_profile_data(user_id)

        if not load_result.success:
            return set_error(load_result.error)

        return load_result.loaded_fields

    except Exception as e:
        return set_error(f"Profile state initialization failed: {str(e)}")


def create_user_profile_update_graph() -> StateGraph:
    """
    Creates the user profile update graph with unified state management.

    Pipeline:
    1. initialize_profile_state: Load current full resume using StateStorageManager
    2. Route based on operation_mode:
       - "update_resume": Direct to resume_updater
       - "parse_linkedin": linkedin_parser → resume_updater
       - "parse_file": file_parser → resume_updater
    3. resume_updater: Merge content and save updated resume

    Returns:
        Compiled LangGraph ready for execution
    """
    # Create graph with simplified state
    graph_builder = StateGraph(UpdateUserProfileState)

    # Add nodes
    graph_builder.add_node("initialize_profile_state", initialize_profile_state)
    graph_builder.add_node("resume_updater", resume_updater)
    graph_builder.add_node("linkedin_parser", linkedin_parser)
    graph_builder.add_node("file_parser", file_parser)

    # Start with state initialization
    graph_builder.add_edge(START, "initialize_profile_state")

    # Route based on operation mode after state initialization
    def route_by_operation_mode(state: UpdateUserProfileState) -> str:
        """Route to appropriate processing node based on operation mode"""
        if state.get("error"):
            return END

        operation_mode = state["operation_mode"]
        if operation_mode == "update_resume":
            return "resume_updater"
        elif operation_mode == "parse_linkedin":
            return "linkedin_parser"
        elif operation_mode == "parse_file":
            return "file_parser"
        else:
            return END

    graph_builder.add_conditional_edges(
        "initialize_profile_state",
        route_by_operation_mode,
        {
            "resume_updater": "resume_updater",
            "linkedin_parser": "linkedin_parser",
            "file_parser": "file_parser",
            END: END,
        },
    )

    # Route parsed content to resume update
    graph_builder.add_edge("linkedin_parser", "resume_updater")
    graph_builder.add_edge("file_parser", "resume_updater")

    # End after resume update
    graph_builder.add_edge("resume_updater", END)

    return graph_builder.compile()


# Create the user profile update graph instance
user_profile_update_graph = create_user_profile_update_graph()
