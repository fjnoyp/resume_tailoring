from langchain_core.tools.base import BaseTool
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from tools.supabase_storage_tools import supabase_storage_tools
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)

async def write_cover_letter(resume_path: str, full_resume_path: str, job_description_path: str, notes_path: str, cover_letter_path: str) -> BaseTool:
    """
    Writes a cover letter for a resume based on recruiter feedback and a job description, saving it as COVER_LETTER.md in Supabase Storage. Use this tool to generate a cover letter that addresses recruiter concerns and highlights the candidate's strengths for the target job.
    
    Args:
        resume_path: Supabase Storage object path to the TAILORED resume (markdown).
        full_resume_path: Supabase Storage object path to the user's full resume (markdown).
        job_description_path: Supabase Storage object path to the job description (markdown).
        notes_path: Supabase Storage object path to recruiter feedback (markdown).
        cover_letter_path: Supabase Storage object path to the cover letter file (markdown).
    
    Returns:
        A concise message explaining the cover letter's focus and that the cover letter file was written. If tool calls fail, a concise error message.
    
    Note: The correct Supabase Storage object paths for all files must be provided as arguments. If you are unsure how to construct these paths, use the get_user_files_paths tool (with the appropriate user_id and job_id) to obtain the canonical paths before calling this tool.
    """
    logging.debug(f"[DEBUG] write_cover_letter tool called with resume_path={resume_path}, full_resume_path={full_resume_path}, job_description_path={job_description_path}, notes_path={notes_path}, cover_letter_path={cover_letter_path}")

    messages = [{"role": "user", "content": f"""
- You are a professional cover letter writer
- The job spec (JOB_DESCRIPTION_PATH), recruiter feedback (NOTES_PATH), the candidate's tailored resume (RESUME_PATH), and full experience history (FULL_RESUME_PATH) will be provided to you, all as markdown files in Supabase Storage.
- Your main goal is to create a cover letter that helps the candidate's overall application for the job spec. Focus on content that addresses recruiter concerns and highlights the candidate's strengths and fit for the role.
- Consider the weaknesses highlighted in the recruiter feedback and how the cover letter can help support or explain any weaknesses indirectly to increase the chance the recruiter accepts the candidate's application.
- Consider the ideal strengths/general experience the candidate has that might not be fully explained in the resume or could be explained more that would help the overall chance for the recruiter to accept the application.
- You may want to add some extra details about the candidate included in the FULL_RESUME_PATH file that would help the application but are not present in the RESUME_PATH file.
- Overall, consider the psychology and goals of the recruiter and how they might assess the application and how this cover letter can help the candidate's overall application.
- Write for brevity (200-500 words max), show do not tell. Consider what makes an ideal cover letter and apply those principles to what you write.
- If possible make it unique in an appropriate way / creatively different that could help attract more attention.

- Use the upload_file_to_bucket tool to write the cover letter to COVER_LETTER_PATH in Supabase Storage. Overwrite if it exists, or create it if it does not. Use the provided COVER_LETTER_PATH argument directly.
- Respond with a concise answer explaining the cover letter's focus and that you have written the full cover letter in the cover letter file.
- If any tool calls fail, respond with a concise error message.

RESUME_PATH: {resume_path}
FULL_RESUME_PATH: {full_resume_path}
JOB_DESCRIPTION_PATH: {job_description_path}
NOTES_PATH: {notes_path}
COVER_LETTER_PATH: {cover_letter_path}
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
        logging.debug("[DEBUG] Agent response in write_cover_letter tool: %s", agent_response["messages"][-1].content)
        return agent_response["messages"][-1].content
    except Exception as e:
        logging.error(f"[DEBUG] Error in write_cover_letter tool: {e}")
        logging.error(traceback.format_exc())
        return None