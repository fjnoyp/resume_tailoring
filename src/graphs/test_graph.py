"""
Test Graph for Resume Tailoring

Mock implementation for frontend testing without token usage.
Simulates the real workflow with predictable responses.
"""

from typing import TypedDict, Optional, List
from langgraph.graph import StateGraph, START, END
from langgraph.types import interrupt


class TestGraphState(TypedDict):
    """Simplified test state matching main graph structure"""

    user_id: str
    job_id: str
    job_description: Optional[str]
    original_resume: Optional[str]
    job_strategy: Optional[str]
    recruiter_feedback: Optional[str]
    tailored_resume: Optional[str]
    messages: List
    error: Optional[str]


def mock_file_loader(state: TestGraphState):
    """Mock file loader - simulates loading files"""
    return {
        "job_description": f"Mock job description for job {state['job_id']}",
        "original_resume": f"Mock original resume for user {state['user_id']}",
    }


def mock_job_analyzer(state: TestGraphState):
    """Mock job analyzer - simulates strategy generation"""
    return {
        "job_strategy": "Mock strategic analysis: Company values innovation and teamwork."
    }


def mock_resume_screener(state: TestGraphState):
    """Mock resume screener - simulates recruiter feedback"""
    return {
        "recruiter_feedback": "Mock recruiter feedback: Strong candidate but needs more backend experience."
    }


def mock_resume_tailorer(state: TestGraphState):
    """Mock resume tailorer - simulates user interaction and tailoring"""
    # Simulate asking the user a question
    answer = interrupt("Mock question: What backend technologies have you used?")

    return {
        "tailored_resume": f"Mock tailored resume incorporating user answer: {answer}",
        "messages": [
            {
                "role": "assistant",
                "content": "Mock question: What backend technologies have you used?",
            },
            {"role": "user", "content": answer},
            {
                "role": "assistant",
                "content": "Thank you! I've incorporated that into your tailored resume.",
            },
        ],
    }


def create_test_graph() -> StateGraph:
    """
    Creates a test graph that mimics the real workflow.

    Returns:
        Compiled test graph for frontend development
    """
    test_workflow = StateGraph(TestGraphState)

    # Add mock nodes
    test_workflow.add_node("file_loader", mock_file_loader)
    test_workflow.add_node("job_analyzer", mock_job_analyzer)
    test_workflow.add_node("resume_screener", mock_resume_screener)
    test_workflow.add_node("resume_tailorer", mock_resume_tailorer)

    # Same structure as main graph
    test_workflow.add_edge(START, "file_loader")
    test_workflow.add_edge("file_loader", "job_analyzer")
    test_workflow.add_edge("job_analyzer", "resume_screener")
    test_workflow.add_edge("resume_screener", "resume_tailorer")
    test_workflow.add_edge("resume_tailorer", END)

    return test_workflow.compile()


# Create test graph instance
test_graph = create_test_graph()
