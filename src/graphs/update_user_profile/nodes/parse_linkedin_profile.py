"""
Parse LinkedIn Profile Node

Parses LinkedIn profile content into structured information.
Pure data processing - no file I/O.
"""

import logging
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from src.llm_config import model
from src.graphs.update_user_profile.state import UpdateUserProfileState, set_error
from src.utils.node_utils import validate_fields, setup_profile_metadata, handle_error

logging.basicConfig(level=logging.DEBUG)


async def parse_linkedin_profile(
    state: UpdateUserProfileState, config: RunnableConfig
) -> Dict[str, Any]:
    """
    Parses LinkedIn profile content into structured information.

    Input: input_data (LinkedIn profile content)
    Output: parsed_content (structured profile information)

    Args:
        state: State containing LinkedIn profile content
        config: LangChain runnable config

    Returns:
        Dictionary with parsed_content or error state
    """
    try:
        # Validate required fields using dot notation
        error_msg = validate_fields(state, ["input_data"], "LinkedIn parsing")
        if error_msg:
            return {"error": error_msg}

        # Extract fields using type-safe dot notation
        user_id = state.user_id
        input_data = state.input_data

        # Setup metadata
        setup_profile_metadata(config, "parse_linkedin_profile", user_id)

        prompt = f"""
Parse this LinkedIn profile content into structured information.

Extract and organize the following information:
- Professional summary/headline
- Work experience (company, role, duration, achievements)
- Education (school, degree, graduation year)
- Skills and endorsements
- Certifications and licenses
- Notable projects or accomplishments
- Contact information

Format the output as clear, structured text that can be easily integrated into a resume.

LINKEDIN_PROFILE:
{input_data}
"""

        # Generate parsed content
        response = await model.ainvoke(prompt, config=config)
        parsed_content = response.content

        logging.debug(f"[DEBUG] LinkedIn profile parsed: {len(parsed_content)} chars")

        return {"parsed_content": parsed_content}

    except Exception as e:
        return handle_error(e, "parse_linkedin_profile")
