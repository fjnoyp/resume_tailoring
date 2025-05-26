"""
Data Loader Node

Handles loading ALL required files from Supabase Storage at the start of the pipeline.
This centralizes ALL file I/O logic and ensures processing nodes have clean separation of concerns.
"""

import logging
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from src.tools.supabase_storage_tools import (
    get_file_paths,
    read_file_from_bucket,
)
from src.state import GraphState, set_error

logging.basicConfig(level=logging.DEBUG)


async def data_loader(state: GraphState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Loads ALL required files from Supabase Storage upfront.

    Loads:
    - job_description: Job posting content
    - original_resume: User's base resume
    - full_resume: User's complete resume with all details

    Args:
        state: Current graph state with user_id and job_id
        config: LangChain runnable config

    Returns:
        Dictionary with all loaded file contents or error state
    """
    try:
        user_id = state["user_id"]
        job_id = state["job_id"]

        # Add metadata for tracing
        config["metadata"] = {
            **config.get("metadata", {}),
            "user_id": user_id,
            "job_id": job_id,
            "node": "data_loader",
        }

        file_paths = get_file_paths(user_id, job_id)

        # Load job description
        job_description = None
        job_description_bytes = await read_file_from_bucket(
            file_paths.job_description_path
        )
        if job_description_bytes:
            job_description = job_description_bytes.decode("utf-8")
            logging.debug(
                f"[DEBUG] Job description loaded: {len(job_description)} chars"
            )

        # Load original resume
        original_resume = None
        resume_bytes = await read_file_from_bucket(file_paths.original_resume_path)
        if resume_bytes:
            original_resume = resume_bytes.decode("utf-8")
            logging.debug(
                f"[DEBUG] Original resume loaded: {len(original_resume)} chars"
            )

        # Load full resume
        full_resume = None
        full_resume_bytes = await read_file_from_bucket(
            file_paths.user_full_resume_path
        )
        if full_resume_bytes:
            full_resume = full_resume_bytes.decode("utf-8")
            logging.debug(f"[DEBUG] Full resume loaded: {len(full_resume)} chars")
        else:
            # Full resume might not exist yet, that's okay
            full_resume = ""
            logging.debug("[DEBUG] Full resume not found, using empty string")

        # Validate required files are present
        if not job_description:
            return set_error(
                f"Job description not found for user {user_id}, job {job_id}"
            )

        if not original_resume:
            return set_error(
                f"Original resume not found for user {user_id}, job {job_id}"
            )

        logging.debug(
            f"[DEBUG] Successfully loaded all data for user {user_id}, job {job_id}"
        )

        return {
            "job_description": job_description,
            "original_resume": original_resume,
            "full_resume": full_resume,
        }

    except Exception as e:
        logging.error(f"[DEBUG] Error in data_loader: {e}")
        return set_error(f"Data loading failed: {str(e)}")
