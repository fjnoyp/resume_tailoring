from langchain_core.tools.base import BaseTool
from src.tools.mcp_agent import invoke_mcp_agent, linkedin_server_params
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)


async def parse_linkedin_profile(linkedin_url: str) -> BaseTool:
    """
    Extracts structured information from a LinkedIn profile URL and returns it as properly formatted markdown. DO NOT use this tool unless the input is a valid LinkedIn web address (e.g., 'https://www.linkedin.com/in/username'). Do not use with file paths or Supabase files named 'linkedin.md' or similar.

    Args:
        linkedin_url: LinkedIn profile URL (must be a valid LinkedIn web address).

    Returns:
        The full, properly formatted markdown content extracted from the LinkedIn profile. Intended for use as info_to_add for full_resume_update_tool. Does not write to storage.
    """
    logging.debug(
        f"[DEBUG] parse_linkedin_profile tool called with linkedin_url={linkedin_url}"
    )

    messages = [
        {
            "role": "user",
            "content": f"""
- You are a professional LinkedIn profile parser
- Your task is to extract structured information from the provided LinkedIn profile
- Focus on extracting:
  * Work experience with dates, roles, and responsibilities
  * Education history
  * Skills and certifications
  * Projects and achievements
  * Recommendations and endorsements
- Return the full, properly formatted markdown content as your response.
- Do not attempt to write to storage or call any upload tools.
- Use only read-only tools to access the source data.

LINKEDIN URL: {linkedin_url}
""",
        }
    ]
    try:
        agent_response = await invoke_mcp_agent(messages, [linkedin_server_params])
        logging.debug(
            "[DEBUG] Agent response in parse_linkedin_profile tool: %s",
            agent_response["messages"][-1:],
        )
        return agent_response["messages"][-1].content
    except Exception as e:
        logging.error(f"[DEBUG] Error in parse_linkedin_profile tool: {e}")
        logging.error(traceback.format_exc())
        return None
