from langchain_core.tools.base import BaseTool
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from src.tools.supabase_storage_tools import read_file_from_bucket
from src.tools.parse_pdf_tool import parse_pdf
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)


async def parse_additional_file(file_path: str) -> BaseTool:
    """
    Extracts structured information from an existing resume or related file in Supabase Storage and returns it as properly formatted markdown. Use this tool to convert a file's content into markdown for further resume updates.

    Args:
        file_path: Supabase Storage path to the file to parse.

    Returns:
        The full, properly formatted markdown content extracted from the file. Intended for use as info_to_add for full_resume_update_tool. Does not write to storage.
    """
    logging.debug(
        f"[DEBUG] parse_additional_file tool called with file_path={file_path}"
    )

    messages = [
        {
            "role": "user",
            "content": f"""
- You are a professional resume experience gatherer from an existing file
- Your task is to extract structured information from the provided file
- Focus on extracting:
  * Work experience with dates, roles, and responsibilities
  * Education history
  * Skills and certifications
  * Projects and achievements
  * Contact information and personal details
- Return the full, properly formatted markdown content as your response.
- Do not attempt to write to storage or call any upload tools.
- Use only read-only tools to access the source data.

EXISTING FILE PATH (extract from this file): {file_path}
""",
        }
    ]

    # Initialize the model
    model = ChatAnthropic(model_name="claude-3-5-sonnet-latest", timeout=120, stop=None)

    try:
        agent = create_react_agent(model, [read_file_from_bucket, parse_pdf])
        agent_response = await agent.ainvoke({"messages": messages})
        # logging.debug("[DEBUG] Agent response in career_info_parser_tool: %s", agent_response["messages"][-1:])
        return agent_response["messages"][-1].content
    except Exception as e:
        logging.error(f"[DEBUG] Error in parse_additional_file tool: {e}")
        logging.error(traceback.format_exc())
        return None
