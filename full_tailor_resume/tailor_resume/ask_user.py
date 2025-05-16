from langchain_core.tools.base import BaseTool
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from tools.supabase_storage_tools import supabase_storage_tools
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)

# TODO: directly interrupt for user input from here instead of passing the questions to the main agent
# also, use the update_user_profile tool to directly write to the "full resume" file
async def ask_user(full_resume_path: str, target_role: str) -> BaseTool:
    """
    Gathers targeted experience details from the user by generating specific questions, guided by the target role. Use this tool to collect new information for a resume, but it does not update or write to any files.
    
    Args:
        full_resume_path: Supabase Storage path to the full resume markdown file (used for context only).
        target_role: Role description to guide the experience gathering questions.
    
    Returns:
        A list of one or more specific, targeted questions as a string or list, to ask the user for further experience details. Does not modify any files.
    
    Note: This tool should be called whenever there's a skill gap or missing experience in the output of the resume_tailoring_tool, in order to gather the missing experience details from the user.
    """
    logging.debug(f"[DEBUG] ask_user tool called with full_resume_path={full_resume_path}, target_role={target_role}")

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
    
    # Initialize the model
    model = ChatAnthropic(
        model_name="claude-3-5-sonnet-latest",
        timeout=120,
        stop=None
    )

    try:
        agent = create_react_agent(model, supabase_storage_tools)
        agent_response = await agent.ainvoke({"messages": messages})
        logging.debug("[DEBUG] Agent response in ask_user tool: %s", agent_response["messages"][-1:])
        return agent_response["messages"][-1].content
    except Exception as e:
        logging.error(f"[DEBUG] Error in ask_user tool: {e}")
        logging.error(traceback.format_exc())
        return None