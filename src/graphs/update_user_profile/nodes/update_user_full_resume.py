"""
Resume Update Node

Merges new information into existing resume content.
Pure data processing - no file I/O.
"""

import logging
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from src.llm_config import model
from src.graphs.update_user_profile.state import UpdateUserProfileState, set_error
from src.tools.state_storage_manager import save_processing_result
from src.utils.node_utils import setup_profile_metadata, handle_error

logging.basicConfig(level=logging.DEBUG)


async def resume_updater(
    state: UpdateUserProfileState, config: RunnableConfig
) -> Dict[str, Any]:
    """
    Merges new information into existing resume content.

    Input: input_data (new information), current_full_resume (loaded by data_loader)
    Output: updated_full_resume

    Args:
        state: Graph state with input data and current resume
        config: LangChain runnable config

    Returns:
        Dictionary with updated_full_resume or error state
    """
    try:
        # Extract fields
        user_id = state["user_id"]
        input_data = state["input_data"]
        current_full_resume = state["current_full_resume"] or ""

        # Handle parsed content if available (from LinkedIn/file parsing)
        content_to_merge = state.get("parsed_content", input_data)

        if not content_to_merge:
            return {"error": "No content available to merge into resume"}

        # Setup metadata
        setup_profile_metadata(config, "resume_updater", user_id)

        prompt = f"""
You are a professional resume writer tasked with updating a user's comprehensive resume.

Your goal is to merge new information into an existing resume while maintaining professional formatting and avoiding duplicates.

Follow these strict guidelines:

1. STRUCTURE:
   - Maintain proper markdown formatting throughout the document
   - Keep existing section headers and structure
   - Add new sections only if they don't exist and are relevant
   - Ensure consistent formatting across all sections

2. CONTENT MERGING:
   - Carefully analyze the new information against existing content
   - Only add non-duplicate information
   - Merge similar experiences/skills into existing entries when appropriate
   - Preserve all existing important information
   - Maintain chronological order in experience/education sections

3. QUALITY CONTROL:
   - Ensure all dates and formatting remain consistent
   - Verify that merged content flows naturally
   - Maintain professional language and tone throughout
   - Remove any redundant or repetitive information

EXISTING RESUME:
{current_full_resume}

NEW INFORMATION TO MERGE:
{content_to_merge}

Return the complete, updated markdown resume with all content properly merged and formatted.
IMPORTANT: Return ONLY the markdown content. Do not include any explanations, comments, or other text before or after the markdown content.
"""

        # Generate updated resume
        response = await model.ainvoke(prompt, config=config)
        updated_full_resume = response.content

        # Save to storage using StateStorageManager
        await save_processing_result(
            user_id, None, "updated_full_resume", updated_full_resume
        )

        logging.debug(f"[DEBUG] Resume updated: {len(updated_full_resume)} chars")

        return {"updated_full_resume": updated_full_resume}

    except Exception as e:
        return handle_error(e, "resume_updater")
