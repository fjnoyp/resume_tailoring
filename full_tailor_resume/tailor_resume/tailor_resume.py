from langchain_core.tools.base import BaseTool
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from tools.supabase_storage_tools import supabase_storage_tools
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)

# TODO: update to include ask_user tool
async def tailor_resume(resume_path: str, full_resume_path: str, notes_path: str, tailored_resume_path: str) -> BaseTool:
    """
    Tailors a resume based on recruiter feedback and the user's full resume, and writes the tailored resume to a new file in Supabase Storage. Use this tool to improve a resume for a specific job based on recruiter analysis and the user's complete experience.
    If you notice any skill gaps or missing experiences in the tool response, you should immediately call the interactive_experience_gathering_tool to gather the missing information from the user.
    
    Args:
        resume_path: Supabase Storage object path to the resume to tailor (markdown).
        full_resume_path: Supabase Storage object path to the user's full resume (markdown).
        notes_path: Supabase Storage object path to recruiter feedback (markdown).
        tailored_resume_path: Supabase Storage object path to the tailored resume file (markdown).
    
    Returns:
        A concise message explaining what was changed and that the tailored resume file was updated. If tool calls fail, a concise error message.
    
    Note: The correct Supabase Storage object paths for all files must be provided as arguments. If you are unsure how to construct these paths, use the get_user_files_paths tool (with the appropriate user_id and job_id) to obtain the canonical paths before calling this tool.
    """
    logging.debug(f"[DEBUG] tailor_resume tool called with resume_path={resume_path}, full_resume_path={full_resume_path}, notes_path={notes_path}, tailored_resume_path={tailored_resume_path}")

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
    
    # Initialize the model
    model = ChatAnthropic(
        model_name="claude-3-5-sonnet-latest",
        timeout=120,
        stop=None
    )
    
    try:
        agent = create_react_agent(model, supabase_storage_tools)
        agent_response = await agent.ainvoke({"messages": messages})
        logging.debug("[DEBUG] Agent response in tailor_resume tool: %s", agent_response["messages"][1:])
        return agent_response["messages"][-1].content
    except Exception as e:
        logging.error(f"[DEBUG] Error in tailor_resume tool: {e}")
        logging.error(traceback.format_exc())
        return None