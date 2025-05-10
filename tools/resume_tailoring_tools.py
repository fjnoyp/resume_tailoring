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

async def resume_screening_tool(resume_path: str, job_description_path: str) -> BaseTool:
    """
    Analyzes a resume against a job description and writes a full analysis in a NOTES.md markdown file at the same file path folder as the provided JOB DESCRIPTION FILE PATH on Supabase Storage.

    Parameters:
    - resume_path (str, required): The Supabase Storage file path (e.g., https://...supabase.co/storage/v1/object/public/...) of the resume to screen.
    - job_description_path (str, required): The Supabase Storage file path of the job description to screen the resume against.

    Returns:
    - str: A concise message explaining the reasoning and recommendation, and that the full analysis was written in the NOTES FILE PATH. If tool calls fail, a concise message explaining what happened.
    """
    logging.debug(f"[DEBUG] resume_screening_tool called with resume_path={resume_path}, job_description_path={job_description_path}")

    messages = [{"role": "user", "content": f"""
- You are a professional recruiter
- You have been given a job spec for a company/role you are recruiting for 
- Assess the resume at RESUME FILE PATH against the job description at JOB DESCRIPTION FILE PATH.
- If it's a good fit for the role, provide pros and cons and reasoning on whether to accept or reject this candidate. 
- Write your thoughts in a well reasoned full analysis of the resume and if it's appropriate for the role you are hiring for 
- Consider that you have 100s of candidates for the same role and you need to be careful on who you accept or not. We cannot accept everyone so it's better to reject candidates and give a rejection answer more aggressively, but important to give full well written reasons on why you want to reject. 
- Provide a markdown-formatted analysis with pros, cons, and a clear accept/reject recommendation.
- Only output markdown.

IMPORTANT:
- Write your full markdown formatted analysis in a NOTES.md file at the same file path folder as the provided JOB DESCRIPTION FILE PATH on Supabase Storage. If the file does not exist, create it with proper markdown formatting. Overwrite if it exists.
- Use the appropriate tool to write the analysis to the NOTES.md file.
- Respond with a concise answer explaining your reasoning and the recommendation and that you have written your full analysis in the NOTES FILE PATH.
- If some of your tool calls fail, respond with a concise answer explaining what happened.

- The file paths provided are Supabase Storage URLs. You can use these directly with your available tools to read the files.
RESUME FILE PATH: {resume_path}
JOB DESCRIPTION FILE PATH: {job_description_path}
NOTES FILE PATH: (same folder as JOB DESCRIPTION FILE PATH, named NOTES.md)
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





async def resume_tailoring_tool(resume_path: str, full_resume_path: str, notes_path: str) -> BaseTool:
    """
    Tailors a resume based on recruiter feedback and the user's full resume and writes the tailored resume to a new TAILORED RESUME.md markdown file at the same file path folder as the provided NOTES FILE PATH on Supabase Storage.

    Parameters:
    - resume_path (str, required): Supabase Storage path to the resume to tailor (markdown)
    - full_resume_path (str, required): Supabase Storage path to the user's full resume (markdown)
    - notes_path (str, required): Supabase Storage path to recruiter feedback (markdown)

    Returns:
    - str: A concise message explaining what was changed and that the RESUME FILE PATH was updated. If tool calls fail, a concise message explaining what happened.
    """
    logging.debug(f"[DEBUG] resume_tailoring_tool called with resume_path={resume_path}, full_resume_path={full_resume_path}, notes_path={notes_path}")

    messages = [{"role": "user", "content": f"""
- You are a professional resume expert.
- In the provided NOTES.md file, you will see a full well written analysis from an AI resume screening recruiter for the role provided on the resume.
- Your task is to take the feedback from this recruiter, paying special attention to addressing any stated 'Cons' or reasons for rejection, and tweak and improve the resume to maximize the likelihood of acceptance.
- Consider all of the points below as you rewrite the resume:

<General Resume Advice>
- The date is 2025 - your internal date is WRONG 

- SHOW DO NOT TELL - don't directly state what the job description is looking for - you need to write about experiences that match it. 

- @resume.md is a good resume that has been vetted by others - your task is to tailor it better to highlight the related experiences that a specific job description might be looking for - you can use @linked-in.md for more information about me. 

- I made an open source ai agentic side project as described in @seren-ai-flutter-readme.md and @seren-ai-langgraph-readme.md and discuss that in @resume.md - regardless of job description it may be good to tweak, shorten, expand, and at the very least, keep this info in any tailored resume as it's an interesting overall experience ... 

- **Customization**: Match skills and experiences to the job description.
- **Clarity**: Use simple, clear language; avoid jargon.
- **Achievements**: Highlight quantifiable results. See @resume.md for examples on how that was done subtly. 
- **Professional Tone**: Maintain professionalism; avoid errors.
- **Keywords**: Use job description keywords for ATS.
- **Format**: Ensure readability with clear structure.
- **Branding**: Emphasize unique skills and goals.
- **Call to Action**: End with enthusiasm and next steps.

## Strategic Application Considerations

- **Recruiter Perspective**: Align with company culture and values.
- **Communication**: Be clear and align strengths with needs.
- **Research**: Understand the company and role.
- **Exaggeration**: Ensure claims are evidence-backed.

- When asked to write a resume always write it into a new resume-kyle-cheng-<company-name>.md like resume-kyle-cheng-hightouch.md etc.
</General Resume Advice>

- **Balance Tailoring with Breadth:** Prioritize aligning the resume's narrative (summary, recent roles, competencies) with the target role's specific requirements and recruiter feedback. *Reframe*, don't remove, broader experiences (AI, Fullstack, Mobile) to highlight transferable skills (system design, API usage, scalability) or showcase unique strengths, especially in projects. Ensure relevance without completely hiding valuable, differentiating skills. Adjust the focus based on role specificity and feedback.

- Draw upon the FULL RESUME file to bring in any missing experiences since that contains all the work experience I have that I didn't always include because the resume cannot be too long - you can also use it to learn more about what makes me a strong candidate etc. 

- You can draw on the fuller experiences written in the FULL RESUME file which includes the non-abridged description of all work experiences. Those details are omitted from the resume as there is too much detail, but you may find some of those details useful for specific roles and can rephrase and add them into the resume you are revising as necessary.
- If there are missing experiences you CANNOT find in the FULL RESUME file, mention them in your response in a section labeled "CANNOT FIND" - the user can possibly provide details on what hasn't been written down yet to aid your rewrite.

- Give reasons in your response explaining how you effectively addressed the recruiter's concerns.

- Always edit the resume file provided to you - do not create a new one. Use the appropriate tool to update the resume file at RESUME FILE PATH. If the file does not exist, create it with proper markdown formatting. Overwrite if it exists.
- Please do not make up experiences, or mischaracterize an experience (e.g., saying the user did backend integration on the Jetbrains AI chat plugin when they didn't, just because the role requires backend experience). Instead, if you identify such gaps or potential misinterpretations based on the available information, mention this clearly in your response.

- Use the edit_file tool to save your revised resume to the resume file provided to you. Do not just say you wrote the file — actually call the tool.
- If you are not given a full resume file, you can use available tools to infer the full resume file in the same folder as the resume file provided to you.

- You've been given tools to read the resume files - use them to read the files and edit the RESUME file provided to you.
- Respond with a concise answer explaining what was changed and that you have updated the RESUME FILE PATH.
- If some of your tool calls fail, respond with a concise answer explaining what happened.
NOTES FILE PATH: {notes_path}
RESUME FILE PATH: {resume_path}
FULL RESUME FILE PATH: {full_resume_path}
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





async def cover_letter_writing_tool(resume_path: str, full_resume_path: str, job_description_path: str, notes_path: str) -> BaseTool:
    """
    Writes a cover letter for a resume based on feedback from a recruiter and a job description into a COVER LETTER.md markdown file at the same file path folder as the provided NOTES FILE PATH on Supabase Storage.

    Parameters:
    - resume_path (str, required): Supabase Storage path to the tailored resume (markdown)
    - full_resume_path (str, required): Supabase Storage path to the user's full resume (markdown)
    - job_description_path (str, required): Supabase Storage path to the job description (markdown)
    - notes_path (str, required): Supabase Storage path to recruiter feedback (markdown)

    Returns:
    - str: A concise message explaining the cover letter's focus and that the full cover letter was written in the COVER LETTER FILE PATH. If tool calls fail, a concise message explaining what happened.
    """
    logging.debug(f"[DEBUG] cover_letter_writing_tool called with resume_path={resume_path}, full_resume_path={full_resume_path}, job_description_path={job_description_path}, notes_path={notes_path}")

    messages = [{"role": "user", "content": f"""
- You are a professional cover letter writer
- The job spec, a NOTES.md feedback from an ai hiring for that job, will be provided to you. 
- Write a COVER_LETTER.md in the same folder as the RESUME file provided to you that helps my overall application for the job spec. 
- Consider the weaknesses highlighted in the NOTES file and how the cover letter can help support or explain any weaknesses indirectly to increase chance recruiter accepts my application
- Consider the ideal strengths/general experience I have that might not be fully explained in the resume or could be explained more that would help my overall chance for recruiter to accept my application 
- You may or may not want to add some extra details about me included in the FULL RESUME file that would help my application but are not present in my RESUME file
- Overall, consider the psychology and goals of the recruiter and how they might assess my application and how this cover letter can help my overall application. 
- You will sometimes be given a sample cover letter to help ground your understanding of what should be written. 
- Write for brevity (200-500 words max), show do not tell. Consider what makes an ideal cover letter and apply those principles to what you write. 
- If possible make it unique in an appropriate way / creatively different that could help attract more attention

- Use the appropriate tool to write the cover letter to COVER LETTER FILE PATH. If the file does not exist, create it with proper markdown formatting. Overwrite if it exists.
- Do not just say you wrote the file — actually call the tool.

- You've been given tools to read the relevant files - use them to read the files and provide your answer in the cover-letter.md file.
- Respond with a concise answer explaining the cover letter's focus and that you have written your full cover letter in the COVER LETTER FILE PATH.
- If some of your tool calls fail, respond with a concise answer explaining what happened.
RESUME FILE PATH: {resume_path}
FULL RESUME FILE PATH: {full_resume_path}
JOB DESCRIPTION FILE PATH: {job_description_path}
NOTES FILE PATH: {notes_path}
COVER LETTER FILE PATH: (same folder as NOTES FILE PATH, named COVER_LETTER.md)
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