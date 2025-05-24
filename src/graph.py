from typing import TypedDict, Annotated, Optional, List
from langgraph.graph.message import add_messages
from langchain_core.runnables import RunnableConfig

# Nodes will be imported directly after modification
from src.analyze_job_description.job_description_analyzer import (
    job_description_analyzer,
)
from src.assess_resume_as_company.resume_screener import resume_screener
from src.tailor_resume.resume_rewriter import resume_rewriter
from langgraph.graph import StateGraph, START, END
from src.state import GraphState, StateManager


# Create the main graph using the hierarchical state
graph_builder = StateGraph(GraphState)

# Nodes are now the actual functions (will be modified to fit signature)
graph_builder.add_node("job_description_analyzer", job_description_analyzer)
graph_builder.add_node("resume_screener", resume_screener)
graph_builder.add_node("resume_rewriter", resume_rewriter)

graph_builder.add_edge(START, "job_description_analyzer")
graph_builder.add_edge("job_description_analyzer", "resume_screener")
graph_builder.add_edge("resume_screener", "resume_rewriter")

graph = graph_builder.compile()


# === TEST GRAPH ===
# Simulates the real workflow with mock nodes to repeatedly test frontend side without spending tokens

from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt, Command


class TestGraphState(TypedDict):
    """Test state using the same structure as main graph for consistency"""

    user_id: str
    job_id: str
    job_strategy: Optional[str]
    recruiter_feedback: Optional[str]
    messages: List


def mock_job_analyzer(state: TestGraphState):
    """First node - just adds some mock data"""
    return {"job_strategy": "Mock strategy for testing"}


def mock_resume_screener(state: TestGraphState):
    """Second node - adds mock feedback"""
    return {"recruiter_feedback": "Mock feedback from recruiter"}


def mock_resume_rewriter(state: TestGraphState):
    """Final node - triggers an interrupt"""
    # This simulates asking the user a question
    count = 1
    should_ask_user = count < 4
    while should_ask_user:
        answer = interrupt(f"Do you want to proceed with these changes ({count})?")
        count += 1
        should_ask_user = count < 4

    return {"messages": [{"content": f"User answered: {answer}", "type": "ai"}]}


"""Creates a test graph that mimics the real workflow but with mock nodes"""
test_workflow = StateGraph(TestGraphState)

# Add our mock nodes
test_workflow.add_node("job_analyzer", mock_job_analyzer)
test_workflow.add_node("resume_screener", mock_resume_screener)
test_workflow.add_node("resume_rewriter", mock_resume_rewriter)

# Add edges - same structure as the real graph
test_workflow.add_edge(START, "job_analyzer")
test_workflow.add_edge("job_analyzer", "resume_screener")
test_workflow.add_edge("resume_screener", "resume_rewriter")
test_workflow.add_edge("resume_rewriter", END)

test_graph = test_workflow.compile()
