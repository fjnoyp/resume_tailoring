"""
LinkedIn Profile Parser Node

Extracts structured information from LinkedIn profiles.
Pure data processing - no file I/O.
"""

import logging
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from src.tools.mcp_agent import invoke_mcp_agent, linkedin_server_params
from src.graphs.update_user_profile.state import UpdateUserProfileState, set_error

logging.basicConfig(level=logging.DEBUG)


async def linkedin_parser(
    state: UpdateUserProfileState, config: RunnableConfig
) -> Dict[str, Any]:
    """
    Extracts structured information from a LinkedIn profile URL.

    Input: input_data (LinkedIn URL)
    Output: parsed_content (structured markdown content)

    Args:
        state: Graph state with LinkedIn URL in input_data
        config: LangChain runnable config

    Returns:
        Dictionary with parsed_content or error state
    """
    try:
        linkedin_url = state["input_data"]

        if not linkedin_url:
            return set_error("No LinkedIn URL provided for parsing")

        # Add metadata for tracing
        config["metadata"] = {
            **config.get("metadata", {}),
            "linkedin_url": linkedin_url,
            "node": "linkedin_parser",
            "graph": "update_user_profile",
        }

        messages = [
            {
                "role": "user",
                "content": f"""
You are a professional LinkedIn profile parser tasked with creating a comprehensive resume section.

Your goal is to extract and structure all relevant professional information from the LinkedIn profile.

Follow these strict guidelines:

1. CONTENT EXTRACTION:
   - Work experience with detailed responsibilities and achievements
   - Education history with degrees, institutions, and dates
   - Skills and certifications with proficiency levels
   - Projects and notable achievements
   - Recommendations and endorsements if relevant
   - Professional summary and headline

2. STRUCTURE:
   - Use clear markdown formatting throughout
   - Organize content into logical sections
   - Maintain chronological order in experience/education
   - Use consistent date formats
   - Include all relevant URLs and references

3. QUALITY CONTROL:
   - Preserve exact job titles and company names
   - Maintain accurate dates and durations
   - Keep professional language and tone
   - Remove any personal contact information
   - Ensure all links and references are professional

LINKEDIN URL:
{linkedin_url}

Return ONLY the properly formatted markdown content. Do not include any explanations, comments, or other text before or after the markdown content.
""",
            }
        ]

        # Parse LinkedIn profile using MCP agent
        agent_response = await invoke_mcp_agent(messages, [linkedin_server_params])
        parsed_content = agent_response["messages"][-1].content

        logging.debug(f"[DEBUG] LinkedIn profile parsed: {len(parsed_content)} chars")

        return {"parsed_content": parsed_content}

    except Exception as e:
        logging.error(f"[DEBUG] Error in linkedin_parser: {e}")
        return set_error(f"LinkedIn parsing failed: {str(e)}")
