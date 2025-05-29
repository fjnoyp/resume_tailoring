"""
Node Utility Functions

Simple utilities for common node operations to reduce code duplication.
"""

import logging
from typing import Dict, Any, List, Union
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel


def validate_fields(
    state: BaseModel, required_fields: List[str], operation: str
) -> str:
    """
    Validate that required fields are present and non-empty in state.

    Args:
        state: Pydantic BaseModel state object
        required_fields: List of field names to validate
        operation: Operation name for error context

    Returns:
        Empty string if valid, error message if invalid
    """
    missing_fields = []

    for field in required_fields:
        try:
            value = getattr(state, field)
            if value is None or (isinstance(value, str) and not value.strip()):
                missing_fields.append(field)
        except AttributeError:
            missing_fields.append(field)

    if missing_fields:
        return f"Missing required fields for {operation}: {', '.join(missing_fields)}"

    return ""


def setup_metadata(
    config: RunnableConfig, node_name: str, user_id: str, job_id: str
) -> None:
    """
    Setup metadata for a node execution.

    Args:
        config: LangChain runnable config
        node_name: Name of the current node
        user_id: User identifier
        job_id: Job identifier
    """
    metadata = config.get("metadata", {})
    metadata.update({"node": node_name, "user_id": user_id, "job_id": job_id})
    config["metadata"] = metadata


def setup_profile_metadata(
    config: RunnableConfig, node_name: str, user_id: str
) -> None:
    """
    Setup metadata for a profile node execution.

    Args:
        config: LangChain runnable config
        node_name: Name of the current node
        user_id: User identifier
    """
    metadata = config.get("metadata", {})
    metadata.update({"node": node_name, "user_id": user_id})
    config["metadata"] = metadata


def handle_error(error: Exception, node_name: str) -> Dict[str, Any]:
    """
    Handle error with consistent logging and return format.

    Args:
        error: The exception that occurred
        node_name: Name of the node where error occurred

    Returns:
        Dictionary with error state
    """
    error_msg = f"Error in {node_name}: {str(error)}"
    logging.error(error_msg, exc_info=True)
    return {"error": error_msg}
