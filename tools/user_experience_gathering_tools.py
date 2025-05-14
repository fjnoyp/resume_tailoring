from langchain_core.tools.base import BaseTool
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from tools.supabase_storage_tools import supabase_storage_tools, read_file_from_bucket
from tools.mcp_servers_tools import invoke_mcp_agent, linkedin_server_params
from tools.parse_pdf_tool import parse_pdf_tool
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)

# Initialize the model
model = ChatAnthropic(
    model_name="claude-3-5-sonnet-latest",
    timeout=120,
    stop=None
)

import logging
import traceback
import os

logging.basicConfig(level=logging.DEBUG)

async def interactive_experience_gathering_tool(full_resume_path: str, target_role: str) -> BaseTool:
    """
    Gathers targeted experience details from the user by generating specific questions, guided by the target role. Use this tool to collect new information for a resume, but it does not update or write to any files.
    
    Args:
        full_resume_path: Supabase Storage path to the full resume markdown file (used for context only).
        target_role: Role description to guide the experience gathering questions.
    
    Returns:
        A list of one or more specific, targeted questions as a string or list, to ask the user for further experience details. Does not modify any files.
    """
    logging.debug(f"[DEBUG] interactive_experience_gathering_tool called with full_resume_path={full_resume_path}, target_role={target_role}")

    messages = [{"role": "user", "content": f"""
- You are an expert career coach and experience gatherer
- Your task is to help gather comprehensive work and project experiences from the user
- If a target role is provided, use it to guide your questions and focus on relevant experiences
- Use a conversational approach to make the user comfortable sharing their experiences
- Proactively ask about:
  * Technical skills and their application in real projects
  * Leadership and collaboration experiences
  * Problem-solving scenarios and their outcomes
  * Quantifiable achievements and metrics
  * Project challenges and how they were overcome
  * Industry-specific experiences relevant to the target role
- Return a list of one or more specific, targeted questions to ask the user in order to gather further experiences or details for their resume.
- Do NOT update or write to the full resume file in this step.
- Do NOT output anything except the questions to ask the user.

FULL RESUME PATH: {full_resume_path}
TARGET ROLE: {target_role}
"""}]
    try:
        agent = create_react_agent(model, supabase_storage_tools)
        agent_response = await agent.ainvoke({"messages": messages})
        # logging.debug("[DEBUG] Agent response in interactive_experience_gathering_tool: %s", agent_response["messages"][-1:])
        # logging.debug("[DEBUG] Agent response in interactive_experience_gathering_tool: %s", agent_response["messages"][-1].content)
        return agent_response["messages"][-1].content
    except Exception as e:
        logging.error(f"[DEBUG] Error in interactive_experience_gathering_tool: {e}")
        logging.error(traceback.format_exc())
        return None
    
async def full_resume_update_tool(full_resume_path: str, info_to_add: str) -> BaseTool:
    """
    Merges new information into the full resume markdown file in Supabase Storage, creating the file if it does not exist. Only adds non-duplicate content and always uploads the full, updated markdown resume.
    
    Args:
        full_resume_path: Supabase Storage path to the full resume markdown file to update or create.
        info_to_add: New information to add, as a markdown string (typically from a parser tool or user answer).
    
    Returns:
        A concise message explaining what was added and that the full resume file was updated or created. If tool calls fail, a concise error message.
    """
    logging.debug(f"[DEBUG] full_resume_update_tool called with full_resume_path={full_resume_path}, info_to_add={info_to_add}")

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
    try:
        agent = create_react_agent(model, supabase_storage_tools)
        agent_response = await agent.ainvoke({"messages": messages})
        logging.debug("[DEBUG] Agent response in full_resume_update_tool: %s", agent_response["messages"][-1:])
        return agent_response["messages"][-1].content
    except Exception as e:
        logging.error(f"[DEBUG] Error in full_resume_update_tool: {e}")
        logging.error(traceback.format_exc())
        return None

async def linkedin_profile_parser_tool(linkedin_url: str) -> str:
    """
    Extracts structured information from a LinkedIn profile URL and returns it as properly formatted markdown. DO NOT use this tool unless the input is a valid LinkedIn web address (e.g., 'https://www.linkedin.com/in/username'). Do not use with file paths or Supabase files named 'linkedin.md' or similar.
    
    Args:
        linkedin_url: LinkedIn profile URL (must be a valid LinkedIn web address).
    
    Returns:
        The full, properly formatted markdown content extracted from the LinkedIn profile. Intended for use as info_to_add for full_resume_update_tool. Does not write to storage.
    """
    logging.debug(f"[DEBUG] linkedin_profile_parser_tool called with linkedin_url={linkedin_url}")

    messages = [{"role": "user", "content": f"""
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
"""}]
    try:
        agent_response = await invoke_mcp_agent(messages, [linkedin_server_params])
        # logging.debug("[DEBUG] Agent response in linkedin_profile_parser_tool: %s", agent_response["messages"][-1:])
        return agent_response["messages"][-1].content
    except Exception as e:
        logging.error(f"[DEBUG] Error in linkedin_profile_parser_tool: {e}")
        logging.error(traceback.format_exc())
        return None

async def career_info_parser_tool(file_path: str) -> str:
    """
    Extracts structured information from an existing resume or related file in Supabase Storage and returns it as properly formatted markdown. Use this tool to convert a file's content into markdown for further resume updates.
    
    Args:
        file_path: Supabase Storage path to the file to parse.
    
    Returns:
        The full, properly formatted markdown content extracted from the file. Intended for use as info_to_add for full_resume_update_tool. Does not write to storage.
    """
    logging.debug(f"[DEBUG] career_info_parser_tool called with file_path={file_path}")

    messages = [{"role": "user", "content": f"""
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
"""}]
    try:
        agent = create_react_agent(model, [read_file_from_bucket, parse_pdf_tool])
        agent_response = await agent.ainvoke({"messages": messages})
        # logging.debug("[DEBUG] Agent response in career_info_parser_tool: %s", agent_response["messages"][-1:])
        return agent_response["messages"][-1].content
    except Exception as e:
        logging.error(f"[DEBUG] Error in career_info_parser_tool: {e}")
        logging.error(traceback.format_exc())
        return None

# List of all user experience gathering tools
user_experience_gathering_tools = [
    interactive_experience_gathering_tool,
    full_resume_update_tool,
    linkedin_profile_parser_tool,
    career_info_parser_tool
]