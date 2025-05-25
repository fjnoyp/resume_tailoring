"""
File Loader Node

Handles loading all required files from Supabase Storage at the start of the pipeline.
This centralizes file I/O logic and ensures other nodes have clean separation of concerns.
"""

import logging
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from src.tools.supabase_storage_tools import (
    get_user_files_paths,
    read_file_from_bucket,
)
from src.state import GraphState, set_error

logging.basicConfig(level=logging.DEBUG)


async def file_loader(state: GraphState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Loads all required files from Supabase Storage.

    Loads:
    - job_description: Job posting content
    - original_resume: User's base resume

    Args:
        state: Current graph state with user_id and job_id
        config: LangChain runnable config

    Returns:
        Dictionary with loaded file contents or error state
    """
    try:
        user_id = state["user_id"]
        job_id = state["job_id"]

        # Add metadata for tracing
        config["metadata"] = {
            **config.get("metadata", {}),
            "user_id": user_id,
            "job_id": job_id,
            "node": "file_loader",
        }

        file_paths = get_user_files_paths(user_id, job_id)

        # Load job description
        job_description = None
        if file_paths.get("job_description_path"):
            job_description_bytes = await read_file_from_bucket(
                file_paths["job_description_path"]
            )
            if job_description_bytes:
                job_description = job_description_bytes.decode("utf-8")
                logging.debug(
                    f"[DEBUG] Job description loaded: {len(job_description)} chars"
                )

        # Load original resume
        original_resume = None
        if file_paths.get("original_resume_path"):
            resume_bytes = await read_file_from_bucket(
                file_paths["original_resume_path"]
            )
            if resume_bytes:
                original_resume = resume_bytes.decode("utf-8")
                logging.debug(
                    f"[DEBUG] Original resume loaded: {len(original_resume)} chars"
                )

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
            f"[DEBUG] Successfully loaded files for user {user_id}, job {job_id}"
        )

        return {"job_description": job_description, "original_resume": original_resume}

    except Exception as e:
        logging.error(f"[DEBUG] Error in file_loader: {e}")
        return set_error(f"File loading failed: {str(e)}")
