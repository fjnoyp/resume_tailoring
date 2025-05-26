from src.update_user_profile.state import FullResumeGraphState
from langchain_core.runnables import RunnableConfig
from src.tools.supabase_storage_tools import get_user_files_paths, read_file_from_bucket, upload_file_to_bucket
from ...main_agent import agent
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)


# TODO: add as a separated "graph" in langgraph.json and call it after gathering info from "ask_user" calls
async def update_user_full_resume(state: FullResumeGraphState, config: RunnableConfig) -> dict:
    """
    Merges new information into the full resume markdown file in Supabase Storage, creating the file if it does not exist. Only adds non-duplicate content.

    Input: input_data (with the new information)
    Output: full_resume (with the updated content)

    Args:
        state: The current graph state.
        config: The LangChain runnable config.

    Returns:
        A dictionary to update the graph state with the full resume.
    """
    try:
        user_id = state["user_id"]
        input_data = state["input_data"]
        full_resume = state.get("full_resume", "")

        # Add metadata to config for tracing/debugging
        config["metadata"] = {
            **config.get("metadata", {}),
            "user_id": user_id,
            "node": "update_user_full_resume"
        }

        if not full_resume:
            file_paths = get_user_files_paths(user_id)
            full_resume_path = file_paths["user_full_resume_path"]
            full_resume_bytes = await read_file_from_bucket(file_paths["user_full_resume_path"]) or b""
            full_resume = full_resume_bytes.decode("utf-8")

        messages = [
            {
                "role": "user",
                "content": f"""
- You are a professional resume writer tasked with updating a user's comprehensive resume
- Your goal is to merge new information into an existing resume while maintaining professional formatting and avoiding duplicates
- Follow these strict guidelines:

1. STRUCTURE:
   - Maintain proper markdown formatting throughout the document
   - Keep existing section headers and structure
   - Add new sections only if they don't exist and are relevant
   - Ensure consistent formatting across all sections

2. CONTENT MERGING:
   - Carefully analyze the new information against existing content
   - Only add non-duplicate information
   - Merge similar experiences/skills into existing entries when appropriate
   - Preserve all existing important information
   - Maintain chronological order in experience/education sections

3. QUALITY CONTROL:
   - Ensure all dates and formatting remain consistent
   - Verify that merged content flows naturally
   - Maintain professional language and tone throughout
   - Remove any redundant or repetitive information

EXISTING RESUME:
{full_resume}

NEW INFORMATION TO MERGE:
{input_data}

Return the complete, updated markdown resume with all content properly merged and formatted.
IMPORTANT: Return ONLY the markdown content. Do not include any explanations, comments, or other text before or after the markdown content.
""",
            }
        ]

        agent_response = await agent.ainvoke(
            {"messages": messages},
            config=config
        )
        logging.debug(
            "[DEBUG] Agent response in update_user_full_resume tool: %s",
            agent_response["messages"][-1:],
        )

        # Extract the updated markdown content from agent response
        updated_content = agent_response["messages"][-1].content
        state["full_resume"] = updated_content

        # Upload the updated full resume to Supabase
        await upload_file_to_bucket(full_resume_path, updated_content)
        logging.debug(
            f"[DEBUG] Updated full resume uploaded to {full_resume_path}"
        )

        # Return the updated state
        return {"full_resume": updated_content, "input_data": ""}
    except Exception as e:
        logging.error(f"[DEBUG] Error in update_user_full_resume. Current state: {state}")
        logging.error(f"[DEBUG] Error in update_user_full_resume tool: {e}")
        logging.error(traceback.format_exc())
        return {"error": f"Error in update_user_full_resume: {str(e)}"}
