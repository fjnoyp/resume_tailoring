from src.tailor_resume.ask_user import ask_user
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from src.tools.supabase_storage_tools import (
    get_user_files_paths,
    upload_file_to_bucket,
    read_file_from_bucket,
)
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)


async def resume_rewriter(inputs: dict) -> str:
    """
    Tailors a resume for a specific job by leveraging recruiter feedback, job description, job strategy, and the user's full resume. Writes the tailored resume to Supabase Storage and returns its content.

    Args:
        user_id: The user's unique identifier.
        job_id: The job's unique identifier.
    Returns:
        The tailored resume content as a string (after writing to Supabase Storage).
    """
    try:
        user_id = inputs["user_id"]
        job_id = inputs["job_id"]

        # Get all relevant file paths
        file_paths = get_user_files_paths(user_id, job_id)
        original_resume_path = file_paths["original_resume_path"]
        full_resume_path = file_paths["user_full_resume_path"]
        recruiter_feedback_path = file_paths["recruiter_feedback_path"]
        job_description_path = file_paths["job_description_path"]
        job_strategy_path = file_paths["job_strategy_path"]
        tailored_resume_path = file_paths["tailored_resume_path"]

        # Read all relevant files from Supabase
        original_resume_bytes = await read_file_from_bucket(original_resume_path) or b""
        full_resume_bytes = await read_file_from_bucket(full_resume_path) or b""
        recruiter_feedback_bytes = (
            await read_file_from_bucket(recruiter_feedback_path) or b""
        )
        job_description_bytes = await read_file_from_bucket(job_description_path) or b""
        job_strategy_bytes = await read_file_from_bucket(job_strategy_path) or b""

        original_resume = original_resume_bytes.decode("utf-8")
        full_resume = full_resume_bytes.decode("utf-8")
        recruiter_feedback = recruiter_feedback_bytes.decode("utf-8")
        job_description = job_description_bytes.decode("utf-8")
        job_strategy = job_strategy_bytes.decode("utf-8")

        message = f"""
- You are a professional resume expert.
- Your task is to rewrite the candidate's resume for the target job, maximizing the likelihood of acceptance.
- First, attempt to tailor the resume using only the ORIGINAL_RESUME, RECRUITER_FEEDBACK, JOB_DESCRIPTION, and JOB_STRATEGY.
- If you detect that required or important experiences/skills are missing or weak, use the FULL_RESUME to search for relevant information and incorporate it into the tailored resume.
- If you still cannot find the required/important experiences/skills in either the original resume or the full resume, call the ask_user tool to gather the missing information directly from the user. You may call this tool multiple times if the user provides incomplete information.
- Only call the ask_user tool if the information is not available in either the original or full resume.
- Write the updated resume as your output (markdown only). Do not make up experiences or mischaracterize the candidate's background. If you identify gaps or potential misinterpretations, mention this clearly in your response.

<General Resume Advice>
- The date is 2025 - your internal date is WRONG
- SHOW DO NOT TELL - don't directly state what the job description is looking for - you need to write about experiences that match it.
- ORIGINAL_RESUME is a good resume that has been vetted by others - your task is to tailor it better to highlight the related experiences that a specific job description might be looking for. If you need more information about the candidate, refer to FULL_RESUME, which contains the complete, detailed work history and additional context.
- **Customization**: Match skills and experiences to the job description.
- **Clarity**: Use simple, clear language; avoid jargon.
- **Achievements**: Highlight quantifiable results. See ORIGINAL_RESUME for examples on how that was done subtly.
- **Professional Tone**: Maintain professionalism; avoid errors.
- **Keywords**: Use job description keywords for ATS.
- **Format**: Ensure readability with clear structure.
- **Branding**: Emphasize unique skills and goals.
</General Resume Advice>

Strategic Application Considerations:
  - **Recruiter Perspective**: Align with company culture and values.
  - **Communication**: Be clear and align strengths with needs.
  - **Research**: Understand the company and role.
  - **Exaggeration**: Ensure claims are evidence-backed.
  - **Balance Tailoring with Breadth:** Prioritize aligning the resume's narrative (summary, recent roles, competencies) with the target role's specific requirements and recruiter feedback. *Reframe*, don't remove, broader experiences (AI, Fullstack, Mobile) to highlight transferable skills (system design, API usage, scalability) or showcase unique strengths, especially in projects. Ensure relevance without completely hiding valuable, differentiating skills. Adjust the focus based on role specificity and feedback.

- Draw upon the FULL_RESUME to bring in any missing experiences since that contains all the work experience the candidate has that was not always included because the resume cannot be too long - you can also use it to learn more about what makes the candidate a strong applicant, etc.
- You can draw on the fuller experiences written in the FULL_RESUME which includes the non-abridged description of all work experiences. Those details are omitted from the resume as there is too much detail, but you may find some of those details useful for specific roles and can rephrase and add them into the resume you are revising as necessary.
- If there are missing experiences or skills that you CANNOT find in the FULL_RESUME, you MUST call the ask_user tool to gather the missing information directly from the user. You may call this tool multiple times if the user provides incomplete information.

- Please do not make up experiences, or mischaracterize an experience (e.g., saying the candidate did backend integration on the Jetbrains AI chat plugin when they didn't, just because the role requires backend experience). Instead, if you identify such gaps or potential misinterpretations based on the available information, mention this clearly in your response.

RECRUITER_FEEDBACK:
{recruiter_feedback}

ORIGINAL_RESUME:
{original_resume}

FULL_RESUME:
{full_resume}

JOB_DESCRIPTION:
{job_description}

JOB_STRATEGY:
{job_strategy}
"""

        # Initialize the model
        model = ChatAnthropic(
            model_name="claude-3-5-sonnet-latest", timeout=120, stop=None
        )
        agent = create_react_agent(model, [ask_user])

        agent_response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": message}]}
        )

        if (
            isinstance(agent_response, dict)
            and agent_response.get("type") == "ask_user"
        ):
            return agent_response  # This will be picked up by the graph for interrupt

        logging.debug(f"[DEBUG] agent_response: {agent_response}")
        tailored_resume = agent_response["messages"][-1]

        # Upload the tailored resume to Supabase
        await upload_file_to_bucket(tailored_resume_path, tailored_resume)
        logging.debug(f"[DEBUG] Tailored resume uploaded to {tailored_resume_path}")

        return tailored_resume
    except Exception as e:
        logging.error(f"[DEBUG] Error in resume_rewriter: {e}")
        logging.error(traceback.format_exc())
        return f"Error: {str(e)}"
