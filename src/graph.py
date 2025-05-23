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

graph = graph_builder.compile()




# Test graph
# simulates the real workflow with mock nodes to repeatedly test frontend side without spending tokens

from typing import TypedDict, Annotated, Optional, List
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command

class TestGraphState(TypedDict):
    user_id: str
    job_id: str
    job_strategy: Optional[str]
    recruiter_feedback: Optional[str]
    messages: List

def mock_job_analyzer(state: TestGraphState):
    """First node - just adds some mock data"""
    return {
        "job_strategy": "Mock strategy for testing"
    }

def mock_resume_screener(state: TestGraphState):
    """Second node - adds mock feedback"""
    return {
        "recruiter_feedback": "Mock feedback from recruiter"
    }

def mock_resume_rewriter(state: TestGraphState):
    """Final node - triggers an interrupt"""
    # This simulates asking the user a question
    count = 1
    should_ask_user = count < 4
    while should_ask_user:
        answer = interrupt(f"Do you want to proceed with these changes ({count})?")
        count += 1
        should_ask_user = count < 4

    return {
        "messages": [
            {
                "content": f"User answered: {answer}",
                "type": "ai"
            }
        ]
    }

"""Creates a test graph that mimics the real workflow but with mock nodes"""
workflow = StateGraph(TestGraphState)

# Add our mock nodes
workflow.add_node("job_analyzer", mock_job_analyzer)
workflow.add_node("resume_screener", mock_resume_screener)
workflow.add_node("resume_rewriter", mock_resume_rewriter)

# Add edges - same structure as the real graph
workflow.add_edge(START, "job_analyzer")
workflow.add_edge("job_analyzer", "resume_screener")
workflow.add_edge("resume_screener", "resume_rewriter")
workflow.add_edge("resume_rewriter", END)

workflow.compile()
