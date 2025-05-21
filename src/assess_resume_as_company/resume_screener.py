from src.tools.supabase_storage_tools import (
    get_user_files_paths,
    upload_file_to_bucket,
    read_file_from_bucket,
)
from ..main_agent import agent
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)


# TODO: after implementing `impersonate_company`, use company-specific info here instead of just a job description
async def resume_screener(inputs: dict) -> str:
    """
    Analyzes a resume against a job description and writes a full markdown analysis to a recruiter feedback file (feedback.md) in Supabase Storage. Use this tool to generate recruiter-style feedback and recommendations for a candidate.
    If any of resume, job_description, or job_strategy is not provided, it is loaded from Supabase Storage using user_id and job_id.

    Args:
        resume: The raw resume text to analyze (optional).
        job_description: The raw job description text to analyze (optional).
        job_strategy: The raw job strategy text to analyze (optional).
        user_id: Unique user identifier.
        job_id: Unique job identifier.

    Returns:
        The generated recruiter feedback (markdown content as a string).
    """
    try:
        user_id = inputs["user_id"]
        job_id = inputs["job_id"]
        file_paths = get_user_files_paths(user_id, job_id)

        if "resume" in inputs:
            job_description = inputs["resume"]
        else:
            resume_path = file_paths["original_resume_path"]
            resume_bytes = await read_file_from_bucket(resume_path) or b""
            resume = resume_bytes.decode("utf-8")

        if "job_description" in inputs:
            job_description = inputs["job_description"]
        else:
            job_description_path = file_paths["job_description_path"]
            job_description_bytes = (
                await read_file_from_bucket(job_description_path) or b""
            )
            job_description = job_description_bytes.decode("utf-8")

        if "job_strategy" in inputs:
            job_strategy = inputs["job_strategy"]
        else:
            job_strategy_path = file_paths["job_strategy_path"]
            job_strategy_bytes = await read_file_from_bucket(job_strategy_path) or b""
            job_strategy = job_strategy_bytes.decode("utf-8")

        message = f"""
- You are a professional recruiter
- You have been given a job spec for a company/role you are recruiting for
- Assess the resume below against the job description below.
- If it's a good fit for the role, provide pros and cons and reasoning on whether to accept or reject this candidate.
- Write your thoughts in a well reasoned full analysis of the resume and if it's appropriate for the role you are hiring for
- Consider that you have 100s of candidates for the same role and you need to be careful on who you accept or not. We cannot accept everyone so it's better to reject candidates and give a rejection answer more aggressively, but important to give full well written reasons on why you want to reject.
- Provide a markdown-formatted analysis with pros, cons, and a clear accept/reject recommendation.
- Only output markdown.

RESUME:
{resume}

JOB_DESCRIPTION:
{job_description}

JOB_STRATEGY:
{job_strategy}
"""
        # Generate the recruiter feedback document
        agent_response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": message}]}
        )
        logging.debug(f"[DEBUG] agent_response: {agent_response}")
        markdown_content = agent_response["messages"][-1].content

        # Upload the recruiter feedback document to the user's job directory in Supabase
        feedback_path = file_paths["recruiter_feedback_path"]
        await upload_file_to_bucket(feedback_path, markdown_content)
        logging.debug(
            f"[DEBUG] Recruiter feedback document uploaded to {feedback_path}"
        )

        return {"user_id": user_id, "job_id": job_id, "content": markdown_content}
    except Exception as e:
        logging.debug(f"[DEBUG] resume_screener inputs: {inputs}")
        logging.error(f"[DEBUG] Error in resume_screener tool: {e}")
        logging.error(traceback.format_exc())
        return f"Error: {str(e)}"
