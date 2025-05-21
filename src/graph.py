from typing import TypedDict, Annotated, Optional, List
from langgraph.graph.message import add_messages
from langchain_core.runnables import RunnableConfig  # Assuming nodes will use this

# Nodes will be imported directly after modification
from src.analyze_job_description.job_description_analyzer import (
    job_description_analyzer,
)
from src.assess_resume_as_company.resume_screener import resume_screener
from src.tailor_resume.resume_rewriter import resume_rewriter
from langgraph.graph import StateGraph, START, END
from src.state import GraphState  # Import GraphState


class GraphState(TypedDict):
    user_id: str
    job_id: str
    job_description: Optional[str] = None
    job_strategy: Optional[str] = None  # Output of job_description_analyzer
    original_resume: Optional[str] = None  # Initial input, or fetched
    # full_resume is fetched internally by resume_rewriter, might not need to be top-level state unless passed initially
    recruiter_feedback: Optional[str] = None  # Output of resume_screener
    tailored_resume: Optional[str] = None  # Output of resume_rewriter

    # For resume_rewriter to communicate questions if it needs to ask the user
    # The content of messages will be managed by resume_rewriter if it needs to ask.
    messages: Annotated[List, add_messages]


graph_builder = StateGraph(GraphState)

# Nodes are now the actual functions (will be modified to fit signature)
graph_builder.add_node("job_description_analyzer", job_description_analyzer)
graph_builder.add_node("resume_screener", resume_screener)
graph_builder.add_node("resume_rewriter", resume_rewriter)

graph_builder.add_edge(START, "job_description_analyzer")
graph_builder.add_edge("job_description_analyzer", "resume_screener")
graph_builder.add_edge("resume_screener", "resume_rewriter")


def is_ask_user(output):
    if isinstance(output, dict):
        return output.get("type") == "ask_user"
    if hasattr(output, "type"):
        return getattr(output, "type") == "ask_user"
    return False


graph_builder.add_conditional_edges(
    "resume_rewriter",
    lambda output: "ask_user" if is_ask_user(output) else END,
    {
        # TODO - add the ask_user node
        "ask_user": END,  # or a node that handles user input
        END: END,
    },
)

graph = graph_builder.compile()
