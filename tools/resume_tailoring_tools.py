from langchain_core.tools.base import BaseTool
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from tools.supabase_storage_tools import supabase_storage_tools
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

logging.basicConfig(level=logging.DEBUG)

async def resume_screening_tool(resume_path: str, job_description_path: str, notes_path: str) -> BaseTool:
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
    logging.debug(f"[DEBUG] resume_screening_tool called with resume_path={resume_path}, job_description_path={job_description_path}, notes_path={notes_path}")

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
    try:
        agent = create_react_agent(model, supabase_storage_tools)
        agent_response = await agent.ainvoke({"messages": messages})
        # logging.debug("[DEBUG] Agent response in resume_screening_tool: %s", agent_response["messages"][1:])
        # logging.debug("[DEBUG] Agent response in resume_screening_tool: %s", agent_response["messages"][-1].content)
        return agent_response["messages"][-1].content
    except Exception as e:
        logging.error(f"[DEBUG] Error in resume_screening_tool: {e}")
        logging.error(traceback.format_exc())
        return None





async def resume_tailoring_tool(resume_path: str, full_resume_path: str, notes_path: str, tailored_resume_path: str) -> BaseTool:
    """
    Tailors a resume based on recruiter feedback and the user's full resume, and writes the tailored resume to a new file (TAILORED_RESUME.md) in Supabase Storage. Use this tool to improve a resume for a specific job based on recruiter analysis and the user's complete experience.
    
    Args:
        resume_path: Supabase Storage object path to the resume to tailor (markdown).
        full_resume_path: Supabase Storage object path to the user's full resume (markdown).
        notes_path: Supabase Storage object path to recruiter feedback (markdown).
        tailored_resume_path: Supabase Storage object path to the tailored resume file (markdown).
    
    Returns:
        A concise message explaining what was changed and that the tailored resume file was updated. If tool calls fail, a concise error message.
    
    Note: The correct Supabase Storage object paths for all files must be provided as arguments. If you are unsure how to construct these paths, use the get_user_files_paths tool (with the appropriate user_id and job_id) to obtain the canonical paths before calling this tool.
    """
    logging.debug(f"[DEBUG] resume_tailoring_tool called with resume_path={resume_path}, full_resume_path={full_resume_path}, notes_path={notes_path}, tailored_resume_path={tailored_resume_path}")

    messages = [{"role": "user", "content": f"""
- You are a professional resume expert.
- In the provided recruiter notes file (NOTES_PATH), you will see a full well written analysis from an AI resume screening recruiter for the role provided on the resume.
- Your task is to take the feedback from this recruiter, paying special attention to addressing any stated 'Cons' or reasons for rejection, and tweak and improve the resume to maximize the likelihood of acceptance.
- Consider all of the points below as you rewrite the resume:

<General Resume Advice>
- The date is 2025 - your internal date is WRONG 
- SHOW DO NOT TELL - don't directly state what the job description is looking for - you need to write about experiences that match it. 
- RESUME_PATH is a good resume that has been vetted by others - your task is to tailor it better to highlight the related experiences that a specific job description might be looking for. If you need more information about the candidate, refer to FULL_RESUME_PATH, which contains the complete, detailed work history and additional context.
- **Customization**: Match skills and experiences to the job description.
- **Clarity**: Use simple, clear language; avoid jargon.
- **Achievements**: Highlight quantifiable results. See RESUME_PATH for examples on how that was done subtly. 
- **Professional Tone**: Maintain professionalism; avoid errors.
- **Keywords**: Use job description keywords for ATS.
- **Format**: Ensure readability with clear structure.
- **Branding**: Emphasize unique skills and goals.
- **Call to Action**: End with enthusiasm and next steps.
</General Resume Advice>

## Strategic Application Considerations

- **Recruiter Perspective**: Align with company culture and values.
- **Communication**: Be clear and align strengths with needs.
- **Research**: Understand the company and role.
- **Exaggeration**: Ensure claims are evidence-backed.
- **Balance Tailoring with Breadth:** Prioritize aligning the resume's narrative (summary, recent roles, competencies) with the target role's specific requirements and recruiter feedback. *Reframe*, don't remove, broader experiences (AI, Fullstack, Mobile) to highlight transferable skills (system design, API usage, scalability) or showcase unique strengths, especially in projects. Ensure relevance without completely hiding valuable, differentiating skills. Adjust the focus based on role specificity and feedback.

- Draw upon the FULL_RESUME_PATH file to bring in any missing experiences since that contains all the work experience the candidate has that was not always included because the resume cannot be too long - you can also use it to learn more about what makes the candidate a strong applicant, etc.
- You can draw on the fuller experiences written in the FULL_RESUME_PATH file which includes the non-abridged description of all work experiences. Those details are omitted from the resume as there is too much detail, but you may find some of those details useful for specific roles and can rephrase and add them into the resume you are revising as necessary.
- If there are missing experiences you CANNOT find in the FULL_RESUME_PATH file, include a section labeled "CANNOT FIND" in your tool response (not in the tailored resume file), listing what is missing so the user can provide details to aid your rewrite.

- Please do not make up experiences, or mischaracterize an experience (e.g., saying the candidate did backend integration on the Jetbrains AI chat plugin when they didn't, just because the role requires backend experience). Instead, if you identify such gaps or potential misinterpretations based on the available information, mention this clearly in your response.

- Use the upload_file_to_bucket tool to write the tailored resume to TAILORED_RESUME_PATH in Supabase Storage. Overwrite if it exists, or create it if it does not. Use the provided TAILORED_RESUME_PATH argument directly.
- Respond with a concise answer explaining what was changed and that you have updated the tailored resume file.
- Give reasons in your response explaining how you effectively addressed the recruiter's concerns.
- If any tool calls fail, respond with a concise error message.

NOTES_PATH: {notes_path}
RESUME_PATH: {resume_path}
FULL_RESUME_PATH: {full_resume_path}
TAILORED_RESUME_PATH: {tailored_resume_path}
"""}]
    try:
        agent = create_react_agent(model, supabase_storage_tools)
        agent_response = await agent.ainvoke({"messages": messages})
        # logging.debug("[DEBUG] Agent response in resume_tailoring_tool: %s", agent_response["messages"][1:])
        # logging.debug("[DEBUG] Agent response in resume_tailoring_tool: %s", agent_response["messages"][-1].content)
        return agent_response["messages"][-1].content
    except Exception as e:
        logging.error(f"[DEBUG] Error in resume_tailoring_tool: {e}")
        logging.error(traceback.format_exc())
        return None





async def cover_letter_writing_tool(resume_path: str, full_resume_path: str, job_description_path: str, notes_path: str, cover_letter_path: str) -> BaseTool:
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
    logging.debug(f"[DEBUG] cover_letter_writing_tool called with resume_path={resume_path}, full_resume_path={full_resume_path}, job_description_path={job_description_path}, notes_path={notes_path}, cover_letter_path={cover_letter_path}")

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
    try:
        agent = create_react_agent(model, supabase_storage_tools)
        agent_response = await agent.ainvoke({"messages": messages})
        # logging.debug("[DEBUG] Agent response in cover_letter_writing_tool: %s", agent_response["messages"][1:])
        # logging.debug("[DEBUG] Agent response in cover_letter_writing_tool: %s", agent_response["messages"][-1].content)
        return agent_response["messages"][-1].content
    except Exception as e:
        logging.error(f"[DEBUG] Error in cover_letter_writing_tool: {e}")
        logging.error(traceback.format_exc())
        return None





resume_tailoring_tools = [resume_screening_tool, resume_tailoring_tool, cover_letter_writing_tool]