from langchain_core.tools.base import BaseTool
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from tools.supabase_storage_tools import supabase_storage_tools
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)

async def update_user_full_resume(full_resume_path: str, info_to_add: str) -> BaseTool:
    """
    Merges new information into the full resume markdown file in Supabase Storage, creating the file if it does not exist. Only adds non-duplicate content and always uploads the full, updated markdown resume.
    
    Args:
        full_resume_path: Supabase Storage path to the full resume markdown file to update or create.
        info_to_add: New information to add, as a markdown string (typically from a parser tool or user answer).
    
    Returns:
        A concise message explaining what was added and that the full resume file was updated or created. If tool calls fail, a concise error message.
    """
    logging.debug(f"[DEBUG] update_user_full_resume tool called with full_resume_path={full_resume_path}, info_to_add={info_to_add}")

    messages = [{"role": "user", "content": f"""

- Merge the provided INFORMATION TO ADD (markdown) into the current content of the full resume at FULL RESUME FILE PATH (also markdown) (if the file exists).
- Only add new, non-duplicate information; do not remove or replace existing content.
- The result must be a complete, well-structured markdown resume, using proper markdown formatting for all sections.
- When calling the upload_file_to_bucket tool, the file_content parameter must be the full, updated markdown resume. Do not pass a summary, description, or explanation — only the actual file content.
- If the file does not exist, create it with properly formatted markdown content.
- **The file_content parameter for the upload must ALWAYS be the full, updated markdown resume.**

- After uploading the file, respond with a concise answer explaining what was added and that you have updated/created the FULL RESUME FILE PATH.
- If some of your tool calls fail, respond with a concise answer explaining what happened.

FULL RESUME FILE PATH: {full_resume_path}
INFORMATION TO ADD: {info_to_add}
"""}]
    
    # Initialize the model
    model = ChatAnthropic(
        model_name="claude-3-5-sonnet-latest",
        timeout=120,
        stop=None
    )

    try:
        agent = create_react_agent(model, supabase_storage_tools)
        agent_response = await agent.ainvoke({"messages": messages})
        logging.debug("[DEBUG] Agent response in update_user_full_resume tool: %s", agent_response["messages"][-1:])
        return agent_response["messages"][-1].content
    except Exception as e:
        logging.error(f"[DEBUG] Error in update_user_full_resume tool: {e}")
        logging.error(traceback.format_exc())
        return None