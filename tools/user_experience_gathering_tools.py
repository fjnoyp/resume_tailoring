from langchain_core.tools.base import BaseTool
from tools.mcp_servers_tools import invoke_mcp_agent, filesystem_server_params, linkedin_server_params

async def interactive_experience_gathering_tool(
    full_resume_path: str,
    target_role: str
) -> BaseTool:
    """
    Interactively gathers user experiences through text input and updates the full resume markdown file.

    Use this tool to gather user experiences from the user whenever you see missing experiences or skills that are relevant to the target role.
    
    - full_resume_path: Path to the full resume markdown file to update
    - target_role: Role description to guide experience gathering
    """
    print(f"[DEBUG] interactive_experience_gathering_tool called with full_resume_path={full_resume_path}, target_role={target_role}")

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
- Update the full resume markdown file with the gathered information
- If the file doesn't exist, create it with proper markdown formatting
- Use the edit_file tool to update the full resume file

- You've been given tools to read and write files - use them to manage the resume data
FULL RESUME PATH: {full_resume_path}
TARGET ROLE: {target_role}
"""}]
    
    try:
        agent_response = await invoke_mcp_agent(messages, [filesystem_server_params])
        # print("[DEBUG] Agent response in interactive_experience_gathering_tool:", agent_response["messages"][1:])
        print("[DEBUG] Agent response in interactive_experience_gathering_tool:", agent_response["messages"][-1].content)
        return agent_response["messages"][-1].content
    except Exception as e:
        print(f"[DEBUG] Error in interactive_experience_gathering_tool: {e}")
        return None

async def linkedin_profile_parser_tool(
    linkedin_url: str,
    full_resume_path: str
) -> BaseTool:
    """
    Parses a LinkedIn profile URL and updates the full resume markdown file with the extracted information.

    This tool can be useful to gather experiences from a LinkedIn profile whenever you see missing experiences or skills that are relevant to the target role.
    
    - linkedin_url: The URL of the LinkedIn profile to parse
    - full_resume_path: Path to the full resume markdown file to update
    """
    print(f"[DEBUG] linkedin_profile_parser_tool called with linkedin_url={linkedin_url}, full_resume_path={full_resume_path}")

    messages = [{"role": "user", "content": f"""
- You are a professional LinkedIn profile parser
- Your task is to extract structured information from the provided LinkedIn profile
- Focus on extracting:
  * Work experience with dates, roles, and responsibilities
  * Education history
  * Skills and certifications
  * Projects and achievements
  * Recommendations and endorsements
- Update the full resume markdown file with the extracted information
- If the file doesn't exist, create it with proper markdown formatting
- Use the edit_file tool to update the full resume file

- You've been given tools to read and write files - use them to manage the resume data
LINKEDIN URL: {linkedin_url}
FULL RESUME PATH: {full_resume_path}
"""}]
    
    try:
        agent_response = await invoke_mcp_agent(messages, [filesystem_server_params, linkedin_server_params])
        # print("[DEBUG] Agent response in linkedin_profile_parser_tool:", agent_response["messages"][1:])
        print("[DEBUG] Agent response in linkedin_profile_parser_tool:", agent_response["messages"][-1].content)
        return agent_response["messages"][-1].content
    except Exception as e:
        print(f"[DEBUG] Error in linkedin_profile_parser_tool: {e}")
        return None

async def resume_parser_tool(
    file_path: str,
    full_resume_path: str
) -> BaseTool:
    """
    Parses an existing file and updates the full resume markdown file with the extracted information.
    
    This tool can be useful to gather experiences from an existing file whenever you see missing experiences or skills that are relevant to the target role.

    - file_path: The path to the file to parse (e.g. resume.md, cover_letter.md, etc.)
    - full_resume_path: Path to the full resume markdown file to update
    """
    print(f"[DEBUG] resume_parser_tool called with file_path={file_path}, full_resume_path={full_resume_path}")

    messages = [{"role": "user", "content": f"""
- You are a professional resume experience gatherer from an existing file
- Your task is to extract structured information from the provided file
- Focus on extracting:
  * Work experience with dates, roles, and responsibilities
  * Education history
  * Skills and certifications
  * Projects and achievements
  * Contact information and personal details
- Update the full resume markdown file with the extracted information
- If the file doesn't exist, create it with proper markdown formatting
- Use the edit_file tool to update the full resume file
- Avoid duplicating information from the existing full resume file

- You've been given tools to read and write files - use them to manage the resume data
EXISTING FILE PATH (extract from this file): {file_path}
FULL RESUME PATH (update this file adding the extracted information): {full_resume_path}
"""}]

    try:
        agent_response = await invoke_mcp_agent(messages, [filesystem_server_params])
        # print("[DEBUG] Agent response in resume_parser_tool:", agent_response["messages"][1:])
        print("[DEBUG] Agent response in resume_parser_tool:", agent_response["messages"][-1].content)
        return agent_response["messages"][-1].content
    except Exception as e:
        print(f"[DEBUG] Error in resume_parser_tool: {e}")
        return None

# List of all user experience gathering tools
user_experience_gathering_tools = [
    interactive_experience_gathering_tool,
    linkedin_profile_parser_tool,
    resume_parser_tool
]