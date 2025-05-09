from langchain_core.tools.base import BaseTool
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from tools.supabase_storage_tools import supabase_storage_tools
from tools.mcp_servers_tools import invoke_mcp_agent, linkedin_server_params
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
Gathers user experiences and updates the full resume markdown file in Supabase Storage.
Returns questions (one or more) to be asked to the user to gather further experiences.

- full_resume_path: Supabase Storage path to the full resume markdown file
- target_role: Role description to guide experience gathering
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
        logging.debug("[DEBUG] Agent response in interactive_experience_gathering_tool: %s", agent_response["messages"][-1:])
        # logging.debug("[DEBUG] Agent response in interactive_experience_gathering_tool: %s", agent_response["messages"][-1].content)
        return agent_response["messages"][-1].content
    except Exception as e:
        logging.error(f"[DEBUG] Error in interactive_experience_gathering_tool: {e}")
        logging.error(traceback.format_exc())
        return None
    
async def full_resume_update_tool(full_resume_path: str, info_to_add: str) -> BaseTool:
    """
Updates the full resume markdown file in Supabase Storage by adding new information.

- full_resume_path: Supabase Storage path to the full resume markdown file
- info_to_add: Information to add to the full resume markdown file
"""
    logging.debug(f"[DEBUG] full_resume_update_tool called with full_resume_path={full_resume_path}, info_to_add={info_to_add}")

    messages = [{"role": "user", "content": f"""
- Add the provided information to the full resume at FULL RESUME FILE PATH.
- Do not remove or replace existing content; only add new information that is not already present.
- Avoid duplicating information that is already in the file.
- Save the updated resume to FULL RESUME FILE PATH.
- Respond with a concise answer explaining what was added and that you have updated the FULL RESUME FILE PATH.
- If some of your tool calls fail, respond with a concise answer explaining what happened.

FULL RESUME FILE PATH: {full_resume_path}
INFORMATION TO ADD: {info_to_add}
"""}]
    try:
        agent = create_react_agent(model, supabase_storage_tools)
        agent_response = await agent.ainvoke({"messages": messages})
        logging.debug("[DEBUG] Agent response in full_resume_update_tool: %s", agent_response["messages"][-1:])
        # logging.debug("[DEBUG] Agent response in full_resume_update_tool: %s", agent_response["messages"][-1].content)
        return agent_response["messages"][-1].content
    except Exception as e:
        logging.error(f"[DEBUG] Error in full_resume_update_tool: {e}")
        logging.error(traceback.format_exc())
        return None

async def linkedin_profile_parser_tool(linkedin_url: str, full_resume_path: str) -> BaseTool:
    """
Parses a LinkedIn profile and updates the full resume markdown file in Supabase Storage by adding new information.

- linkedin_url: LinkedIn profile URL
- full_resume_path: Supabase Storage path to the full resume markdown file
"""
    logging.debug(f"[DEBUG] linkedin_profile_parser_tool called with linkedin_url={linkedin_url}, full_resume_path={full_resume_path}")

    messages = [{"role": "user", "content": f"""
- You are a professional LinkedIn profile parser
- Your task is to extract structured information from the provided LinkedIn profile
- Focus on extracting:
  * Work experience with dates, roles, and responsibilities
  * Education history
  * Skills and certifications
  * Projects and achievements
  * Recommendations and endorsements
- Add the extracted information to the full resume at FULL RESUME FILE PATH.
- Do not remove or replace existing content; only add new information that is not already present.
- Avoid duplicating information that is already in the file.
- If the file doesn't exist, create it with proper markdown formatting.
- Respond with a concise answer explaining what was added and that you have updated the FULL RESUME FILE PATH.
- If some of your tool calls fail, respond with a concise answer explaining what happened.

LINKEDIN URL: {linkedin_url}
FULL RESUME FILE PATH: {full_resume_path}
"""}]
    try:
        agent_response = await invoke_mcp_agent(messages, [linkedin_server_params], additional_tools=supabase_storage_tools)
        logging.debug("[DEBUG] Agent response in linkedin_profile_parser_tool: %s", agent_response["messages"][-1:])
        # logging.debug("[DEBUG] Agent response in linkedin_profile_parser_tool: %s", agent_response["messages"][-1].content)
        return agent_response["messages"][-1].content
    except Exception as e:
        logging.error(f"[DEBUG] Error in linkedin_profile_parser_tool: {e}")
        logging.error(traceback.format_exc())
        return None

async def resume_parser_tool(file_path: str, full_resume_path: str) -> BaseTool:
    """
Parses an existing resume (or experience/skills related) file and updates the full resume markdown file in Supabase Storage by adding new information.

- file_path: Supabase Storage path to the file to parse
- full_resume_path: Supabase Storage path to the full resume markdown file
"""
    logging.debug(f"[DEBUG] resume_parser_tool called with file_path={file_path}, full_resume_path={full_resume_path}")

    messages = [{"role": "user", "content": f"""
- You are a professional resume experience gatherer from an existing file
- Your task is to extract structured information from the provided file
- Focus on extracting:
  * Work experience with dates, roles, and responsibilities
  * Education history
  * Skills and certifications
  * Projects and achievements
  * Contact information and personal details
- Add the extracted information to the full resume at FULL RESUME FILE PATH.
- Do not remove or replace existing content; only add new information that is not already present.
- Avoid duplicating information that is already in the file.
- If the file doesn't exist, create it with proper markdown formatting.
- Use the edit_file tool to update the full resume file.
- Respond with a concise answer explaining what was added and that you have updated the FULL RESUME FILE PATH.
- If some of your tool calls fail, respond with a concise answer explaining what happened.

EXISTING FILE PATH (extract from this file): {file_path}
FULL RESUME FILE PATH: {full_resume_path}
"""}]
    try:
        agent = create_react_agent(model, supabase_storage_tools)
        agent_response = await agent.ainvoke({"messages": messages})
        logging.debug("[DEBUG] Agent response in resume_parser_tool: %s", agent_response["messages"][-1:])
        # logging.debug("[DEBUG] Agent response in resume_parser_tool: %s", agent_response["messages"][-1].content)
        return agent_response["messages"][-1].content
    except Exception as e:
        logging.error(f"[DEBUG] Error in resume_parser_tool: {e}")
        logging.error(traceback.format_exc())
        return None

# List of all user experience gathering tools
user_experience_gathering_tools = [
    interactive_experience_gathering_tool,
    full_resume_update_tool,
    linkedin_profile_parser_tool,
    resume_parser_tool
]