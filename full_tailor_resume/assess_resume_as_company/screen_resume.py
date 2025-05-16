from langchain_core.tools.base import BaseTool
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from tools.supabase_storage_tools import supabase_storage_tools
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)

# TODO: after implementing `impersonate_company`, use company-specific info here instead of just a job description
async def screen_resume(resume_path: str, job_description_path: str, notes_path: str) -> BaseTool:
    """
    Analyzes a resume against a job description and writes a full markdown analysis to a recruiter notes file (NOTES.md) in Supabase Storage. Use this tool to generate recruiter-style feedback and recommendations for a candidate.
    
    Args:
        resume_path: Supabase Storage object path to the resume to screen (markdown).
        job_description_path: Supabase Storage object path to the job description (markdown).
        notes_path: Supabase Storage object path to the recruiter notes file (markdown).
    
    Returns:
        A concise message explaining the reasoning and recommendation, and that the full analysis was written to the recruiter notes file. If tool calls fail, a concise error message.
    
    Note: The correct Supabase Storage object paths for all files must be provided as arguments. If you are unsure how to construct these paths, use the get_user_files_paths tool (with the appropriate user_id and job_id) to obtain the canonical paths before calling this tool.
    """
    logging.debug(f"[DEBUG] screen_resume tool called with resume_path={resume_path}, job_description_path={job_description_path}, notes_path={notes_path}")

    messages = [{"role": "user", "content": f"""
- You are a professional recruiter
- You have been given a job spec for a company/role you are recruiting for 
- Assess the resume at RESUME_PATH against the job description at JOB_DESCRIPTION_PATH.
- If it's a good fit for the role, provide pros and cons and reasoning on whether to accept or reject this candidate. 
- Write your thoughts in a well reasoned full analysis of the resume and if it's appropriate for the role you are hiring for 
- Consider that you have 100s of candidates for the same role and you need to be careful on who you accept or not. We cannot accept everyone so it's better to reject candidates and give a rejection answer more aggressively, but important to give full well written reasons on why you want to reject. 
- Provide a markdown-formatted analysis with pros, cons, and a clear accept/reject recommendation.
- Only output markdown.

IMPORTANT:
- Write your full markdown formatted analysis to the recruiter notes file at NOTES_PATH in Supabase Storage. If the file does not exist, create it with proper markdown formatting. Overwrite if it exists. Use the provided NOTES_PATH argument directly.
- Use the upload_file_to_bucket tool to write the analysis to the recruiter notes file.
- Respond with a concise answer explaining your reasoning and the recommendation and that you have written your full analysis in the recruiter notes file.
- If any tool calls fail, respond with a concise error message.

RESUME_PATH: {resume_path}
JOB_DESCRIPTION_PATH: {job_description_path}
NOTES_PATH: {notes_path}
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
        logging.debug("[DEBUG] Agent response in screen_resume tool: %s", agent_response["messages"][1:])
        return agent_response["messages"][-1].content
    except Exception as e:
        logging.error(f"[DEBUG] Error in screen_resume tool: {e}")
        logging.error(traceback.format_exc())
        return None