from src.tools.mcp_agent import invoke_mcp_agent, linkedin_server_params
from src.update_user_profile.state import FullResumeGraphState
from langchain_core.runnables import RunnableConfig
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)


async def parse_linkedin_profile(state: FullResumeGraphState, config: RunnableConfig) -> dict:
    """
    Extracts structured information from a LinkedIn profile URL and returns it as properly formatted markdown.

    Input: input_data (with the LinkedIn URL)
    Output: input_data (with the parsed LinkedIn profile content)

    Args:
        state: The current graph state.
        config: The LangChain runnable config.

    Returns:
        A dictionary containing the parsed LinkedIn content in the input_data field, ready for the next node in the graph.
    """
    try:
        linkedin_url = state["input_data"]

        # Add metadata to config for tracing/debugging
        config["metadata"] = {
            **config.get("metadata", {}),
            "linkedin_url": linkedin_url,
            "node": "parse_linkedin_profile"
        }

        messages = [
            {
                "role": "user",
                "content": f"""
- You are a professional LinkedIn profile parser tasked with creating a comprehensive resume section
- Your goal is to extract and structure all relevant professional information from the LinkedIn profile
- Follow these strict guidelines:

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

        agent_response = await invoke_mcp_agent(messages, [linkedin_server_params])
        logging.debug(
            "[DEBUG] Agent response in parse_linkedin_profile tool: %s",
            agent_response["messages"][-1:],
        )

        # Extract the markdown content from agent response
        parsed_content = agent_response["messages"][-1].content
        
        # Return updated state
        return {"input_data": parsed_content}

    except Exception as e:
        logging.error(f"[DEBUG] Error in parse_linkedin_profile. Current state: {state}")
        logging.error(f"[DEBUG] Error in parse_linkedin_profile tool: {e}")
        logging.error(traceback.format_exc())
        return {"error": f"Error in parse_linkedin_profile: {str(e)}"}
