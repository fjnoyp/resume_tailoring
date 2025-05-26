from langchain_anthropic import ChatAnthropic
from src.tools.supabase_storage_tools import (
    upload_file_to_bucket,
)
import logging
import traceback
from typing import Optional, Tuple

logging.basicConfig(level=logging.DEBUG)


async def update_user_full_resume(
    full_resume_path: str, current_full_resume: str, info_to_add: str
) -> Optional[Tuple[str, str]]:
    """
    Merges new information into the full resume content and uploads to Supabase Storage.

    Args:
        full_resume_path: Supabase Storage path to upload the updated resume
        current_full_resume: Current full resume content (passed from caller)
        info_to_add: New information to add, as a markdown string

    Returns:
        Tuple of (summary_message, updated_resume_content) if successful, None if failed
    """
    logging.debug(
        f"[DEBUG] update_user_full_resume called with full_resume_path={full_resume_path}, "
        f"current_full_resume={len(current_full_resume)} chars, info_to_add={len(info_to_add)} chars"
    )

    # Initialize the model
    model = ChatAnthropic(model_name="claude-3-5-sonnet-latest", timeout=120)

    try:
        prompt = f"""
You are a professional resume expert. Your task is to merge new information into an existing resume while maintaining proper markdown formatting.

EXISTING RESUME:
{current_full_resume}

INFORMATION TO ADD:
{info_to_add}

Instructions:
1. Merge the new information into the existing resume
2. Only add new, non-duplicate content
3. Maintain proper markdown formatting
4. Create a complete, well-structured resume if none exists
5. Return ONLY the complete updated resume content, no explanations

Return the complete updated resume content in markdown format.
"""

        # Get updated resume content from model
        response = await model.ainvoke(prompt)
        updated_resume = response.content

        # Upload the updated resume
        await upload_file_to_bucket(full_resume_path, updated_resume)

        # Generate summary of changes
        summary_prompt = f"""
Summarize what new information was added to the resume in one concise sentence.
Focus only on what was added, not the full content.

EXISTING RESUME:
{current_full_resume}

UPDATED RESUME:
{updated_resume}
"""
        summary_response = await model.ainvoke(summary_prompt)
        summary = summary_response.content

        summary_message = f"{summary} Full resume updated at {full_resume_path}"
        return (summary_message, updated_resume)

    except Exception as e:
        logging.error(f"[DEBUG] Error in update_user_full_resume: {e}")
        logging.error(traceback.format_exc())
        return None
