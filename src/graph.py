"""
Main Resume Tailoring Graph

Clean, linear pipeline for resume tailoring:
START → data_loader → job_analyzer → resume_screener → resume_tailorer → END
"""

from langgraph.graph import StateGraph, START, END
from src.state import GraphState
from src.nodes import data_loader, job_analyzer, resume_screener, resume_tailorer


def create_graph() -> StateGraph:
    """
    Creates the main resume tailoring graph.

    Pipeline:
    1. data_loader: Loads ALL files (job description, original resume, full resume) from storage
    2. job_analyzer: Analyzes job to extract company strategy and requirements
    3. resume_screener: Evaluates resume from recruiter perspective
    4. resume_tailorer: Tailors resume using all analysis results

    Returns:
        Compiled LangGraph ready for execution
    """
    # Create graph with simplified flat state
    graph_builder = StateGraph(GraphState)

    # Add processing nodes in pipeline order
    graph_builder.add_node("data_loader", data_loader)
    graph_builder.add_node("job_analyzer", job_analyzer)
    graph_builder.add_node("resume_screener", resume_screener)
    graph_builder.add_node("resume_tailorer", resume_tailorer)

    # Define linear pipeline
    graph_builder.add_edge(START, "data_loader")
    graph_builder.add_edge("data_loader", "job_analyzer")
    graph_builder.add_edge("job_analyzer", "resume_screener")
    graph_builder.add_edge("resume_screener", "resume_tailorer")
    graph_builder.add_edge("resume_tailorer", END)

    return graph_builder.compile()


# Create the main graph instance
graph = create_graph()
