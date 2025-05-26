"""
User Full Resume Update Graph

Handles different ways to update a user's full resume:
1. Direct update from new information
2. Parse LinkedIn profile and merge
3. Parse additional files and merge
"""

from langgraph.graph import StateGraph, START
from src.update_user_profile.nodes.update_user_full_resume import update_user_full_resume
from src.update_user_profile.nodes.parse_linkedin_profile import parse_linkedin_profile
from src.update_user_profile.nodes.parse_file_to_markdown import parse_file_to_markdown
from src.update_user_profile.state import FullResumeGraphState, AiBehaviorMode


def create_user_full_resume_graph() -> StateGraph:
    """
    Creates the user full resume update graph.

    Pipeline:
    1. Routes to appropriate node based on AI behavior mode
    2. Parses information from LinkedIn or additional files if needed
    3. Updates full resume with new information

    Returns:
        Compiled LangGraph ready for execution
    """
    # Create graph with full resume state
    graph_builder = StateGraph(FullResumeGraphState)

    # Add processing nodes
    graph_builder.add_node("update_user_full_resume", update_user_full_resume)
    graph_builder.add_node("parse_linkedin_profile", parse_linkedin_profile)
    graph_builder.add_node("parse_additional_file", parse_file_to_markdown)

    # Route based on AI behavior mode
    def edge_route_by_ai_behavior_mode(state: FullResumeGraphState):
        return state["ai_behavior_mode"]

    graph_builder.add_conditional_edges(
        START,
        edge_route_by_ai_behavior_mode,
        {
            AiBehaviorMode.UPDATE_USER_FULL_RESUME.value: "update_user_full_resume",
            AiBehaviorMode.PARSE_LINKEDIN_PROFILE.value: "parse_linkedin_profile",
            AiBehaviorMode.PARSE_ADDITIONAL_FILE.value: "parse_additional_file",
        },
    )

    # Route parsed information to resume update
    graph_builder.add_edge("parse_linkedin_profile", "update_user_full_resume")
    graph_builder.add_edge("parse_additional_file", "update_user_full_resume")

    return graph_builder.compile()


# Create the user full resume graph instance
user_full_resume_graph = create_user_full_resume_graph()