from langchain_core.tools.base import BaseTool
from filesystem_mcp_server_tools import invoke_filesystem_mcp_agent
from prompts.general_resume_advice_prompt import GENERAL_RESUME_ADVICE_PROMPT

async def resume_screening_tool(resume_path: str, job_description_path: str) -> BaseTool:
    """
Writes a full analysis of a resume against a job description into a file titled NOTES.md in the same folder of the resume given to you.

- resume_path: The path to the file containing the resume to screen
- job_description_path: The path to the file containing the job description to screen the resume against
"""
    print(f"[DEBUG] resume_screening_tool called with resume_path={resume_path}, job_description_path={job_description_path}")

    messages = [{"role": "user", "content": f"""
- You are a professional recruiter 
- You have been given a job spec for a company/role you are recruiting for 
- Take the given resume and assess if it's a good fit for the role, provide pros and cons and reasoning on whether to accept or reject this candidate. 
- Write your thoughts in a well reasoned full analysis of the resume and if it's appropriate for the role you are hiring for 
- Consider that you have 100s of candidates for the same role and you need to be careful on who you accept or not. We cannot accept everyone so it's better to reject candidates and give a rejection answer more aggressively, but important to give full well written reasons on why you want to reject. 
- We will continue rewriting the resume based on your feedback, so always review the latest resume given to you to provide fresh up to date comments 

- Use the write_file tool to save your answer to NOTES.md. Do not just say you wrote the file — actually call the tool.

- You've been given tools to read the job description and resume - use them to read the files and provide your response in the NOTES.md file
JOB DESCRIPTION FILE PATH: {job_description_path}
RESUME FILE PATH: {resume_path}
"""}]
    try:
        print("[DEBUG] Agent created. About to invoke agent with messages...")
        agent_response = await invoke_filesystem_mcp_agent(messages)
        print("[DEBUG] Agent response in resume_screening_tool.call_tool:", agent_response["messages"][1:])
        return agent_response["messages"][-1].content
    except Exception as e:
        print(f"[DEBUG] Error in resume_screening_tool.call_tool: {e}")
        return None





async def resume_tailoring_tool(resume_path: str, full_resume_path: str, notes_path: str) -> BaseTool:
    """
Takes the feedback from a recruiter on a resume and edits the resume based on the feedback.

- notes_path: The path to the file containing the feedback from the recruiter
- resume_path: The path to the file containing the resume to tailor
- full_resume_path: The path to the file containing the full resume that includes the non-abridged description of all work experiences
"""
    print(f"[DEBUG] resume_tailoring_tool called with resume_path={resume_path}, full_resume_path={full_resume_path}, notes_path={notes_path}")

    messages = [{"role": "user", "content": f"""
- You are a professional resume expert.
- In the provided NOTES.md file, you will see a full well written analysis from an AI resume screening recruiter for the role provided on the resume.
- Your task is to take the feedback from this recruiter, paying special attention to addressing any stated 'Cons' or reasons for rejection, and tweak and improve the resume to maximize the likelihood of acceptance.
- Consider all of the points below as you rewrite the resume:

{GENERAL_RESUME_ADVICE_PROMPT}



- **Balance Tailoring with Breadth:** Prioritize aligning the resume's narrative (summary, recent roles, competencies) with the target role's specific requirements and recruiter feedback. *Reframe*, don't remove, broader experiences (AI, Fullstack, Mobile) to highlight transferable skills (system design, API usage, scalability) or showcase unique strengths, especially in projects. Ensure relevance without completely hiding valuable, differentiating skills. Adjust the focus based on role specificity and feedback.

- Draw upon the FULL RESUME file to bring in any missing experiences since that contains all the work experience I have that I didn't always include because the resume cannot be too long - you can also use it to learn more about what makes me a strong candidate etc. 

- You can draw on the fuller experiences written in the FULL RESUME file which includes the non-abridged description of all work experiences. Those details are omitted from the resume as there is too much detail, but you may find some of those details useful for specific roles and can rephrase and add them into the resume you are revising as necessary.
- If there are missing experiences you CANNOT find in the FULL RESUME file, mention them in your response in a section labeled "CANNOT FIND" - the user can possibly provide details on what hasn't been written down yet to aid your rewrite.

- Give reasons in your response explaining how you effectively addressed the recruiter's concerns.

- Always edit the resume file provided to you - do not create a new one.

- Please do not make up experiences, or mischaracterize an experience (e.g., saying the user did backend integration on the Jetbrains AI chat plugin when they didn't, just because the role requires backend experience). Instead, if you identify such gaps or potential misinterpretations based on the available information, mention this clearly in your response.

- Use the edit_file tool to save your revised resume to the resume file provided to you. Do not just say you wrote the file — actually call the tool.

- You've been given tools to read the resume files - use them to read the files and edit the RESUME file provided to you.
NOTES FILE PATH: {notes_path}
RESUME FILE PATH: {resume_path}
FULL RESUME FILE PATH: {full_resume_path}
"""}]
    agent_response = await invoke_filesystem_mcp_agent(messages)
    print("[DEBUG] Agent response in resume_tailoring_tool.call_tool:", agent_response["messages"][1:])
    return agent_response["messages"][-1].content





async def cover_letter_writing_tool(resume_path: str, full_resume_path: str, job_description_path: str, notes_path: str) -> BaseTool:
    """
Writes a cover letter for a resume based on feedback from a recruiter and a job description.

- resume_path: The path to the file containing the resume to write the cover letter for
- full_resume_path: The path to the file containing the full resume that includes the non-abridged description of all work experiences
- job_description_path: The path to the file containing the job description to write the cover letter for
- notes_path: The path to the file containing the feedback from the recruiter
"""
    print(f"[DEBUG] cover_letter_writing_tool called with resume_path={resume_path}, full_resume_path={full_resume_path}, job_description_path={job_description_path}, notes_path={notes_path}")

    messages = [{"role": "user", "content": f"""
- You are a professional cover letter writer
- The job spec, a NOTES.md feedback from an ai hiring for that job, will be provided to you. 
- Write a cover-letter.md in the same folder as the RESUME file provided to you that helps my overall application for the job spec. 
- Consider the weaknesses highlighted in the NOTES file and how the cover letter can help support or explain any weaknesses indirectly to increase chance recruiter accepts my application
- Consider the ideal strengths/general experience I have that might not be fully explained in the resume or could be explained more that would help my overall chance for recruiter to accept my application 
- You may or may not want to add some extra details about me included in the FULL RESUME file that would help my application but are not present in my RESUME file
- Overall, consider the psychology and goals of the recruiter and how they might assess my application and how this cover letter can help my overall application. 
- You will sometimes be given a sample cover letter to help ground your understanding of what should be written. 
- Write for brevity (200-500 words max), show do not tell. Consider what makes an ideal cover letter and apply those principles to what you write. 
- If possible make it unique in an appropriate way / creatively different that could help attract more attention

- Use the write_file tool to save your answer to cover-letter.md. Do not just say you wrote the file — actually call the tool.

- You've been given tools to read the relevant files - use them to read the files and provide your response in the cover-letter.md file
JOB DESCRIPTION FILE PATH: {job_description_path}
NOTES FILE PATH: {notes_path}
RESUME FILE PATH: {resume_path}
FULL RESUME FILE PATH: {full_resume_path}
"""}]
    agent_response = await invoke_filesystem_mcp_agent(messages)
    print("[DEBUG] Agent response in cover_letter_writing_tool.call_tool:", agent_response["messages"][1:])
    return agent_response["messages"][-1].content





resume_tailoring_tools = [resume_screening_tool, resume_tailoring_tool, cover_letter_writing_tool]