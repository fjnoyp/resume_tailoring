from typing import TypedDict, Annotated, Optional, List, Dict, Any
from langgraph.graph.message import add_messages
from dataclasses import dataclass
from enum import Enum


# === IMMUTABLE CONTEXT ===
class SessionContext(TypedDict):
    """Immutable session data - never changes after graph initialization"""

    user_id: str
    job_id: str


# === MUTABLE DOMAIN DATA ===
class JobDomain(TypedDict):
    """Job-related information and processing results"""

    description: Optional[str]  # Input or loaded from storage
    strategy: Optional[str]  # Output of job_description_analyzer


class ResumeDomain(TypedDict):
    """Resume content and analysis results"""

    original: Optional[str]  # Input or loaded from storage
    tailored: Optional[str]  # Output of resume_rewriter
    recruiter_feedback: Optional[str]  # Output of resume_screener


class InteractionDomain(TypedDict):
    """User interaction and conversation state"""

    messages: Annotated[List, add_messages]
    pending_question: Optional[str]  # For GraphInterrupt flow
    interaction_type: Optional[str]  # For conditional logic


class ErrorDomain(TypedDict):
    """Error tracking and debugging information"""

    last_error: Optional[str]
    error_context: Optional[Dict[str, Any]]


# === MAIN STATE ===
class GraphState(TypedDict):
    """
    Domain-separated state with clear boundaries:
    - context: Immutable session data
    - job: Job-related processing pipeline
    - resume: Resume-related processing pipeline
    - interaction: User communication and flow control
    - errors: Error tracking for debugging
    """

    context: SessionContext
    job: JobDomain
    resume: ResumeDomain
    interaction: InteractionDomain
    errors: ErrorDomain


# === STATE MANAGEMENT UTILITIES ===
class StateManager:
    """
    Centralized state management with domain-specific helpers.
    Encapsulates state access patterns and provides type-safe updates.
    """

    @staticmethod
    def create_initial_state(user_id: str, job_id: str) -> GraphState:
        """Create a new state with all required fields initialized"""
        return {
            "context": {
                "user_id": user_id,
                "job_id": job_id,
            },
            "job": {
                "description": None,
                "strategy": None,
            },
            "resume": {
                "original": None,
                "tailored": None,
                "recruiter_feedback": None,
            },
            "interaction": {
                "messages": [],
                "pending_question": None,
                "interaction_type": None,
            },
            "errors": {
                "last_error": None,
                "error_context": None,
            },
        }

    # === CONTEXT ACCESSORS (Read-only) ===
    @staticmethod
    def get_user_id(state: GraphState) -> str:
        """Get user ID from immutable context"""
        return state["context"]["user_id"]

    @staticmethod
    def get_job_id(state: GraphState) -> str:
        """Get job ID from immutable context"""
        return state["context"]["job_id"]

    # === JOB DOMAIN HELPERS ===
    @staticmethod
    def get_job_description(state: GraphState) -> Optional[str]:
        """Get current job description"""
        return state["job"]["description"]

    @staticmethod
    def get_job_strategy(state: GraphState) -> Optional[str]:
        """Get current job strategy"""
        return state["job"]["strategy"]

    @staticmethod
    def set_job_description(state: GraphState, description: str) -> Dict[str, Any]:
        """Update job description (returns partial state for LangGraph merge)"""
        return {"job": {**state["job"], "description": description}}

    @staticmethod
    def set_job_strategy(state: GraphState, strategy: str) -> Dict[str, Any]:
        """Update job strategy (for job_description_analyzer node)"""
        return {"job": {**state["job"], "strategy": strategy}}

    # === RESUME DOMAIN HELPERS ===
    @staticmethod
    def get_original_resume(state: GraphState) -> Optional[str]:
        """Get original resume content"""
        return state["resume"]["original"]

    @staticmethod
    def get_tailored_resume(state: GraphState) -> Optional[str]:
        """Get tailored resume content"""
        return state["resume"]["tailored"]

    @staticmethod
    def get_recruiter_feedback(state: GraphState) -> Optional[str]:
        """Get recruiter feedback"""
        return state["resume"]["recruiter_feedback"]

    @staticmethod
    def set_original_resume(state: GraphState, resume: str) -> Dict[str, Any]:
        """Update original resume content"""
        return {"resume": {**state["resume"], "original": resume}}

    @staticmethod
    def set_recruiter_feedback(state: GraphState, feedback: str) -> Dict[str, Any]:
        """Update recruiter feedback (for resume_screener node)"""
        return {"resume": {**state["resume"], "recruiter_feedback": feedback}}

    @staticmethod
    def set_tailored_resume(state: GraphState, tailored_resume: str) -> Dict[str, Any]:
        """Update tailored resume (for resume_rewriter node)"""
        return {"resume": {**state["resume"], "tailored": tailored_resume}}

    # === INTERACTION DOMAIN HELPERS ===
    @staticmethod
    def get_messages(state: GraphState) -> List:
        """Get conversation messages"""
        return state["interaction"]["messages"]

    @staticmethod
    def get_pending_question(state: GraphState) -> Optional[str]:
        """Get pending user question"""
        return state["interaction"]["pending_question"]

    @staticmethod
    def set_messages(state: GraphState, messages: List) -> Dict[str, Any]:
        """Update conversation messages"""
        return {"interaction": {**state["interaction"], "messages": messages}}

    @staticmethod
    def set_user_question(
        state: GraphState, question: str, interaction_type: str = "question"
    ) -> Dict[str, Any]:
        """Set a pending question for GraphInterrupt flow"""
        return {
            "interaction": {
                **state["interaction"],
                "pending_question": question,
                "interaction_type": interaction_type,
            }
        }

    @staticmethod
    def clear_user_question(state: GraphState) -> Dict[str, Any]:
        """Clear pending question after user response"""
        return {
            "interaction": {
                **state["interaction"],
                "pending_question": None,
                "interaction_type": None,
            }
        }

    # === ERROR HANDLING ===
    @staticmethod
    def set_error(
        state: GraphState, error_msg: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record an error with optional context"""
        return {"errors": {"last_error": error_msg, "error_context": context or {}}}

    @staticmethod
    def clear_error(state: GraphState) -> Dict[str, Any]:
        """Clear error state"""
        return {"errors": {"last_error": None, "error_context": None}}

    @staticmethod
    def has_error(state: GraphState) -> bool:
        """Check if there's a current error"""
        return state["errors"]["last_error"] is not None

    # === BULK OPERATIONS ===
    @staticmethod
    def bulk_update(state: GraphState, **updates) -> Dict[str, Any]:
        """
        Update multiple domains at once.
        Usage: StateManager.bulk_update(state, job_strategy="...", original_resume="...")
        """
        result = {}

        # Job domain updates
        if any(key.startswith("job_") for key in updates.keys()):
            job_updates = {}
            if "job_description" in updates:
                job_updates["description"] = updates["job_description"]
            if "job_strategy" in updates:
                job_updates["strategy"] = updates["job_strategy"]
            if job_updates:
                result["job"] = {**state["job"], **job_updates}

        # Resume domain updates
        if any(
            key.startswith("resume_")
            or key in ["original_resume", "tailored_resume", "recruiter_feedback"]
            for key in updates.keys()
        ):
            resume_updates = {}
            if "original_resume" in updates:
                resume_updates["original"] = updates["original_resume"]
            if "tailored_resume" in updates:
                resume_updates["tailored"] = updates["tailored_resume"]
            if "recruiter_feedback" in updates:
                resume_updates["recruiter_feedback"] = updates["recruiter_feedback"]
            if resume_updates:
                result["resume"] = {**state["resume"], **resume_updates}

        # Interaction domain updates
        if any(
            key.startswith("interaction_") or key in ["messages", "pending_question"]
            for key in updates.keys()
        ):
            interaction_updates = {}
            if "messages" in updates:
                interaction_updates["messages"] = updates["messages"]
            if "pending_question" in updates:
                interaction_updates["pending_question"] = updates["pending_question"]
            if "interaction_type" in updates:
                interaction_updates["interaction_type"] = updates["interaction_type"]
            if interaction_updates:
                result["interaction"] = {**state["interaction"], **interaction_updates}

        return result


# === LEGACY COMPATIBILITY HELPERS ===
class LegacyStateAdapter:
    """
    Backward compatibility helpers for gradual migration.
    Maps old flat field names to new hierarchical structure.
    """

    @staticmethod
    def get_flat_field(state: GraphState, field_name: str) -> Any:
        """Get field using old flat naming convention"""
        field_mapping = {
            "user_id": lambda s: s["context"]["user_id"],
            "job_id": lambda s: s["context"]["job_id"],
            "job_description": lambda s: s["job"]["description"],
            "job_strategy": lambda s: s["job"]["strategy"],
            "original_resume": lambda s: s["resume"]["original"],
            "tailored_resume": lambda s: s["resume"]["tailored"],
            "recruiter_feedback": lambda s: s["resume"]["recruiter_feedback"],
            "messages": lambda s: s["interaction"]["messages"],
            "pending_question": lambda s: s["interaction"]["pending_question"],
            "error": lambda s: s["errors"]["last_error"],
        }

        if field_name in field_mapping:
            return field_mapping[field_name](state)
        else:
            raise KeyError(f"Unknown legacy field: {field_name}")

    @staticmethod
    def set_flat_field(
        state: GraphState, field_name: str, value: Any
    ) -> Dict[str, Any]:
        """Set field using old flat naming convention"""
        field_mapping = {
            "job_description": lambda s, v: StateManager.set_job_description(s, v),
            "job_strategy": lambda s, v: StateManager.set_job_strategy(s, v),
            "original_resume": lambda s, v: StateManager.set_original_resume(s, v),
            "tailored_resume": lambda s, v: StateManager.set_tailored_resume(s, v),
            "recruiter_feedback": lambda s, v: StateManager.set_recruiter_feedback(
                s, v
            ),
            "messages": lambda s, v: StateManager.set_messages(s, v),
            "error": lambda s, v: StateManager.set_error(s, v),
        }

        if field_name in field_mapping:
            return field_mapping[field_name](state, value)
        else:
            raise KeyError(f"Cannot set legacy field: {field_name}")


# === CONVENIENCE ALIASES ===
# Short aliases for common operations
SM = StateManager
LSA = LegacyStateAdapter
