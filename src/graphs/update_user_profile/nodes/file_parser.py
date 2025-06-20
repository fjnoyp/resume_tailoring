"""
File Parser Node

Extracts structured information from files and converts to markdown.
Pure data processing - no file I/O.
"""

import logging
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from src.tools.state_data_manager import StateDataManager
from src.tools.parse_document_tool import parse_document
from src.llm_config import model
from src.graphs.update_user_profile.state import UpdateUserProfileState, set_error
from src.utils.node_utils import validate_fields, setup_profile_metadata, handle_error

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
        # Validate required fields using dot notation
        error_msg = validate_fields(state, ["input_data"], "file parsing")
        if error_msg:
            return {"error": error_msg}

        # Extract fields using type-safe dot notation
        user_id = state.user_id
        file_names_str = state.input_data
        file_names = [name.strip() for name in file_names_str.split(",")]

        # Setup metadata
        setup_profile_metadata(config, "file_parser", user_id)

        # Read all files content using StateDataManager
        all_content = []
        missing_files = []
        original_resume_content = None  # Track if we find an ORIGINAL_RESUME file
        
        for file_name in file_names:
            # Read file bytes for potential PDF processing
            file_content_bytes = await StateDataManager.read_temp_file_bytes(
                user_id, file_name
            )

            if not file_content_bytes:
                logging.error(f"[DEBUG] File not found in temp storage: {file_name} for user {user_id}")
                logging.error(f"[DEBUG] Expected path: {user_id}/temp/{file_name}")
                missing_files.append(file_name)
                continue

            # Handle different file types
            file_extension = file_name.lower().split('.')[-1]
            if file_extension in ['pdf', 'docx', 'doc']:
                file_content = await parse_document(file_content_bytes, file_extension) or ""
            else:
                file_content = file_content_bytes.decode("utf-8")

            # Check if this is an ORIGINAL_RESUME file (any extension)
            file_name_without_ext = file_name.rsplit('.', 1)[0].upper()
            if file_name_without_ext == "ORIGINAL_RESUME":
                original_resume_content = file_content
                logging.debug(f"[DEBUG] Detected ORIGINAL_RESUME file: {file_name}, will update original_resume field")

            all_content.append(f"Content from {file_name}:\n{file_content}")
            logging.debug(f"[DEBUG] Successfully read file: {file_name}, content length: {len(file_content)}")

        if not all_content:
            error_msg = f"No valid file content found to parse. Missing files: {missing_files}. " \
                       f"Files should be uploaded to temp storage at paths: " \
                       f"{[f'{user_id}/temp/{f}' for f in missing_files]}"
            logging.error(f"[DEBUG] {error_msg}")
            return {"error": error_msg}

        # Save original resume if we found one
        if original_resume_content:
            from src.tools.state_data_manager import save_processing_result
            await save_processing_result(user_id, None, "original_resume", original_resume_content)
            logging.debug(f"[DEBUG] Updated original_resume field with content from ORIGINAL_RESUME file")

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

        # Delete all files from temp storage
        for file_name in file_names:
            logging.debug(f"[DEBUG] Deleting file from temp storage: {file_name}")
            try:
                await StateDataManager.delete_temp_file(user_id, file_name)
            except Exception as e:
                logging.error(f"[DEBUG] Error deleting file from temp storage: {e}")

        return {"parsed_content": parsed_content}

    except Exception as e:
        return handle_error(e, "file_parser")
