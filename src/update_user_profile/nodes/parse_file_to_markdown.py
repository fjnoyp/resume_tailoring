"""
File Parser Node

Extracts structured information from files and converts to markdown.
Pure data processing - no file I/O.
"""

import logging
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from src.tools.supabase_storage_tools import read_file_from_bucket, get_file_paths
from src.tools.parse_pdf_tool import parse_pdf
from src.main_agent import model
from src.update_user_profile.state import UpdateUserProfileState, set_error

logging.basicConfig(level=logging.DEBUG)


async def file_parser(
    state: UpdateUserProfileState, config: RunnableConfig
) -> Dict[str, Any]:
    """
    Extracts structured information from files and converts to markdown.

    Input: input_data (comma-separated file names)
    Output: parsed_content (structured markdown content)

    Args:
        state: Graph state with file names in input_data
        config: LangChain runnable config

    Returns:
        Dictionary with parsed_content or error state
    """
    try:
        file_names_str = state["input_data"]
        user_id = state["user_id"]

        if not file_names_str:
            return set_error("No file names provided for parsing")

        file_names = [name.strip() for name in file_names_str.split(",")]

        # Add metadata for tracing
        config["metadata"] = {
            **config.get("metadata", {}),
            "file_names": file_names,
            "user_id": user_id,
            "node": "file_parser",
            "graph": "update_user_profile",
        }

        # Get the base path structure
        file_paths = get_file_paths(user_id, "")  # Empty job_id for user files

        # Read all files content
        all_content = []
        for file_name in file_names:
            # Construct file path for user's additional files
            file_path = f"{user_id}/{file_name}"
            file_content_bytes = await read_file_from_bucket(file_path)

            if not file_content_bytes:
                logging.warning(f"File not found: {file_path}")
                continue

            # Handle PDF files differently
            if file_name.lower().endswith(".pdf"):
                file_content = await parse_pdf(file_content_bytes) or ""
            else:
                file_content = file_content_bytes.decode("utf-8")

            all_content.append(f"Content from {file_name}:\n{file_content}")

        if not all_content:
            return set_error("No valid file content found to parse")

        combined_content = "\n\n---\n\n".join(all_content)

        prompt = f"""
You are a professional resume parser tasked with extracting comprehensive career information.

Your goal is to convert the provided document(s) into a well-structured resume format.

Follow these strict guidelines:

1. CONTENT EXTRACTION:
   - Work experience with detailed responsibilities and achievements
   - Education history with degrees, institutions, and dates
   - Technical skills and certifications with proficiency levels
   - Projects and notable achievements
   - Professional summary and key qualifications
   - Relevant volunteer work or extracurricular activities

2. STRUCTURE:
   - Use clear markdown formatting throughout
   - Organize content into logical sections
   - Maintain chronological order in experience/education
   - Use consistent date formats
   - Preserve formatting for lists and bullet points

3. QUALITY CONTROL:
   - Maintain accurate job titles and company names
   - Preserve exact dates and durations
   - Keep professional language and tone
   - Remove any redundant information
   - Ensure consistent formatting across sections
   - Merge information from multiple sources without duplication

SOURCE CONTENT:
{combined_content}

Return ONLY the properly formatted markdown content. Do not include any explanations, comments, or other text before or after the markdown content.
"""

        # Parse file content using model
        response = await model.ainvoke(prompt, config=config)
        parsed_content = response.content

        logging.debug(
            f"[DEBUG] Files parsed: {len(parsed_content)} chars from {len(file_names)} files"
        )

        return {"parsed_content": parsed_content}

    except Exception as e:
        logging.error(f"[DEBUG] Error in file_parser: {e}")
        return set_error(f"File parsing failed: {str(e)}")
