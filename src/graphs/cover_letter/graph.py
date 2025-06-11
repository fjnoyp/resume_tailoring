"""
Cover Letter Generation Graph

Separate workflow for cover letter generation and evaluation:
START → load_cover_letter_data → cover_letter_generator → END

This graph assumes the resume tailoring has already been completed and loads
the required data from the database/storage.
"""

from langgraph.graph import StateGraph, START, END
from src.graphs.cover_letter.state import CoverLetterState, set_error
from src.graphs.cover_letter.nodes import cover_letter_generator
from src.tools.state_data_manager import StateDataManager, StateLoadMode


async def load_cover_letter_data(state: CoverLetterState, config) -> dict:
    """
    Load required data for cover letter generation using StateDataManager.
    
    Loads:
    - job_description from database
    - tailored_resume from database  
    - recruiter_feedback from database
    - full_resume from database
    """
    try:
        # Extract fields using dot notation
        user_id = state.user_id
        job_id = state.job_id

        # Add metadata for tracing
        config["metadata"] = {
            **config.get("metadata", {}),
            "user_id": user_id,
            "job_id": job_id,
            "node": "load_cover_letter_data",
        }

        # Load required data from database using StateDataManager
        load_result = await StateDataManager.load_state_data(
            user_id, job_id, mode=StateLoadMode.COVER_LETTER
        )

        if not load_result.success:
            return set_error(f"Failed to load cover letter data: {load_result.error}")

        # Validate required fields are present
        required_fields = ["job_description", "tailored_resume", "recruiter_feedback", "full_resume"]
        missing = [f for f in required_fields if not load_result.loaded_fields.get(f)]
        
        if missing:
            return set_error(f"Missing required fields for cover letter generation: {missing}")

        return load_result.loaded_fields

    except Exception as e:
        return set_error(f"Cover letter data loading failed: {str(e)}")





def create_cover_letter_graph() -> StateGraph:
    """
    Creates the cover letter generation graph.

    Pipeline:
    1. load_cover_letter_data: Load required data from database
    2. cover_letter_generator: Generate cover letter based on tailored resume and feedback

    Returns:
        Compiled LangGraph ready for execution
    """
    # Create graph
    graph_builder = StateGraph(CoverLetterState)

    # Add nodes
    graph_builder.add_node("load_cover_letter_data", load_cover_letter_data)
    graph_builder.add_node("cover_letter_generator", cover_letter_generator)

    # Define pipeline
    graph_builder.add_edge(START, "load_cover_letter_data")
    graph_builder.add_edge("load_cover_letter_data", "cover_letter_generator")
    graph_builder.add_edge("cover_letter_generator", END)

    return graph_builder.compile()


# Create the cover letter graph instance
cover_letter_graph = create_cover_letter_graph() 