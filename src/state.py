from typing import TypedDict, Annotated, Optional, List
from langgraph.graph.message import add_messages


class GraphState(TypedDict):
    user_id: str
    job_id: str
    job_description: Optional[str] = None
    job_strategy: Optional[str] = None  # Output of job_description_analyzer
    original_resume: Optional[str] = (
        None  # Initial input, or fetched from Supabase by nodes
    )
    # full_resume is fetched internally by resume_rewriter
    recruiter_feedback: Optional[str] = None  # Output of resume_screener
    tailored_resume: Optional[str] = None  # Output of resume_rewriter

    # messages will accumulate the conversation, including AI questions and user responses
    messages: Annotated[List, add_messages]

    # Optional field to indicate if resume_rewriter needs to ask a question
    # This helps the conditional edge in graph.py
    ask_user_query: Optional[str] = None  # The question to ask the user

    # Type field for conditional logic, used by resume_rewriter if it needs to ask a question.
    # This will be checked by the is_ask_user function in graph.py
    type: Optional[str] = None
