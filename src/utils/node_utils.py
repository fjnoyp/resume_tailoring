"""
Simple Node Utilities

Minimal helpers to reduce code duplication in nodes.
"""

import logging
from typing import Dict, Any, List, Optional
from langchain_core.runnables import RunnableConfig


def validate_fields(
    state: Dict[str, Any], required_fields: List[str], context: str = ""
) -> Optional[str]:
    """
    Validate required fields exist and are not empty.

    Returns:
        Error message if validation fails, None if successful
    """
    missing = [field for field in required_fields if not state.get(field)]
    if missing:
        context_suffix = f" for {context}" if context else ""
        return f"Missing required fields: {', '.join(missing)}{context_suffix}"
    return None


def setup_metadata(
    config: RunnableConfig,
    node_name: str,
    user_id: str,
    job_id: Optional[str] = None,
    **extra,
) -> None:
    """
    Setup metadata for tracing.
    """
    metadata = {
        **config.get("metadata", {}),
        "user_id": user_id,
        "node": node_name,
    }
    if job_id:
        metadata["job_id"] = job_id
    metadata.update(extra)
    config["metadata"] = metadata


def setup_profile_metadata(
    config: RunnableConfig, node_name: str, user_id: str, **extra
) -> None:
    """
    Setup metadata for profile update nodes.
    """
    metadata = {
        **config.get("metadata", {}),
        "user_id": user_id,
        "node": node_name,
        "graph": "update_user_profile",
    }
    metadata.update(extra)
    config["metadata"] = metadata


def handle_error(error: Exception, node_name: str, context: str = "") -> Dict[str, Any]:
    """
    Handle node errors consistently.
    """
    context_suffix = f" in {context}" if context else ""
    error_msg = (
        f"{node_name.replace('_', ' ').title()} failed{context_suffix}: {str(error)}"
    )
    logging.error(f"[DEBUG] Error in {node_name}: {error}")
    return {"error": error_msg}
