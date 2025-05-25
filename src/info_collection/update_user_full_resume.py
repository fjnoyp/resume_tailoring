from langchain_anthropic import ChatAnthropic
from src.tools.supabase_storage_tools import (
    read_file_from_bucket,
    upload_file_to_bucket,
)
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)


async def update_user_full_resume(full_resume_path: str, info_to_add: str) -> str:
    """
    Merges new information into the full resume markdown file in Supabase Storage, creating the file if it does not exist. Only adds non-duplicate content and always uploads the full, updated markdown resume.

    Args:
        full_resume_path: Supabase Storage path to the full resume markdown file to update or create.
        info_to_add: New information to add, as a markdown string (typically from a parser tool or user answer).

    Returns:
        A concise message explaining what was added and that the full resume file was updated or created. If tool calls fail, a concise error message.
    """
    logging.debug(
        f"[DEBUG] update_user_full_resume called with full_resume_path={full_resume_path}, info_to_add={info_to_add}"
    )

    # Initialize the model
    model = ChatAnthropic(model_name="claude-3-5-sonnet-latest", timeout=120)

    try:
        # Read existing resume if it exists
        existing_resume_bytes = await read_file_from_bucket(full_resume_path)
        existing_resume = (
            existing_resume_bytes.decode("utf-8") if existing_resume_bytes else ""
        )

        prompt = f"""
You are a professional resume expert. Your task is to merge new information into an existing resume while maintaining proper markdown formatting.

EXISTING RESUME:
{existing_resume}

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
{existing_resume}

UPDATED RESUME:
{updated_resume}
"""
        summary_response = await model.ainvoke(summary_prompt)
        summary = summary_response.content

        return f"{summary} Full resume updated at {full_resume_path}"

    except Exception as e:
        logging.error(f"[DEBUG] Error in update_user_full_resume: {e}")
        logging.error(traceback.format_exc())
        return None
