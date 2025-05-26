"""
Data Loader Node for User Profile Updates

Handles loading the user's current full resume from Supabase Storage.
This centralizes file I/O logic for the update_user_profile graph.
"""

import logging
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from src.tools.supabase_storage_tools import (
    get_file_paths,
    read_file_from_bucket,
)
from src.update_user_profile.state import UpdateUserProfileState, set_error

logging.basicConfig(level=logging.DEBUG)


async def data_loader(
    state: UpdateUserProfileState, config: RunnableConfig
) -> Dict[str, Any]:
    """
    Loads the user's current full resume from Supabase Storage.

    Args:
        state: Current graph state with user_id
        config: LangChain runnable config

    Returns:
        Dictionary with current_full_resume content or error state
    """
    try:
        user_id = state["user_id"]

        # Add metadata for tracing
        config["metadata"] = {
            **config.get("metadata", {}),
            "user_id": user_id,
            "node": "data_loader",
            "graph": "update_user_profile",
        }

        file_paths = get_file_paths(user_id, "")  # Empty job_id for user files

        # Load current full resume
        current_full_resume = ""
        full_resume_bytes = await read_file_from_bucket(
            file_paths.user_full_resume_path
        )
        if full_resume_bytes:
            current_full_resume = full_resume_bytes.decode("utf-8")
            logging.debug(
                f"[DEBUG] Current full resume loaded: {len(current_full_resume)} chars"
            )
        else:
            # Full resume might not exist yet, that's okay
            logging.debug("[DEBUG] Full resume not found, starting with empty content")

        logging.debug(
            f"[DEBUG] Successfully loaded data for user {user_id} in update_user_profile"
        )

        return {"current_full_resume": current_full_resume}

    except Exception as e:
        logging.error(f"[DEBUG] Error in update_user_profile data_loader: {e}")
        return set_error(f"Data loading failed: {str(e)}")
