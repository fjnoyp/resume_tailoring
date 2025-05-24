from src.tools.supabase_storage_tools import (
    get_user_files_paths,
    upload_file_to_bucket,
    read_file_from_bucket,
)
from ..main_agent import agent
import logging
import traceback
from src.state import GraphState, StateManager
from langchain_core.runnables import RunnableConfig

logging.basicConfig(level=logging.DEBUG)


# TODO: after implementing `impersonate_company`, use company-specific info here instead of just a job description
async def resume_screener(state: GraphState, config: RunnableConfig) -> dict:
    """
    Analyzes a resume against a job description and writes a full markdown analysis to a recruiter feedback file (feedback.md) in Supabase Storage. Use this tool to generate recruiter-style feedback and recommendations for a candidate.
    If any of resume, job_description, or job_strategy is not provided from state, it is loaded from Supabase Storage using user_id and job_id from state.

    Args:
        state: The current graph state.
        config: The LangChain runnable config.

    Returns:
        A dictionary to update the graph state with recruiter_feedback.
    """
    try:
        # Use StateManager for clean access to context
        user_id = StateManager.get_user_id(state)
        job_id = StateManager.get_job_id(state)
        file_paths = get_user_files_paths(user_id, job_id)

        # Add metadata to config for tracing/debugging
        config["metadata"] = {
            **config.get("metadata", {}),
            "user_id": user_id,
            "job_id": job_id,
            "node": "resume_screener",
        }

        # Load required data from state or storage
        resume = StateManager.get_original_resume(state)
        if not resume:
            resume_path = file_paths["original_resume_path"]
            resume_bytes = await read_file_from_bucket(resume_path) or b""
            resume = resume_bytes.decode("utf-8")

        job_description = StateManager.get_job_description(state)
        if not job_description:
            job_description_path = file_paths["job_description_path"]
            job_description_bytes = (
                await read_file_from_bucket(job_description_path) or b""
            )
            job_description = job_description_bytes.decode("utf-8")

        job_strategy = StateManager.get_job_strategy(state)
        if not job_strategy:
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
            {"messages": [{"role": "user", "content": message}]}, config=config
        )
        logging.debug(f"[DEBUG] agent_response: {agent_response}")
        markdown_content = agent_response["messages"][-1].content

        # Upload the recruiter feedback document to the user's job directory in Supabase
        feedback_path = file_paths["recruiter_feedback_path"]
        await upload_file_to_bucket(feedback_path, markdown_content)
        logging.debug(
            f"[DEBUG] Recruiter feedback document uploaded to {feedback_path}"
        )

        # Use StateManager for clean bulk update - store any loaded data + new feedback
        return StateManager.bulk_update(
            state,
            original_resume=resume,
            job_description=job_description,
            job_strategy=job_strategy,
            recruiter_feedback=markdown_content,
        )

    except Exception as e:
        # Log the state for debugging purposes if an error occurs
        logging.error(
            f"[DEBUG] Error in resume_screener. Current state context: user_id={StateManager.get_user_id(state)}, job_id={StateManager.get_job_id(state)}"
        )
        logging.error(f"[DEBUG] Error in resume_screener tool: {e}")
        logging.error(traceback.format_exc())

        # Use StateManager for standardized error handling
        return StateManager.set_error(
            state,
            f"Error in resume_screener: {str(e)}",
            {
                "user_id": StateManager.get_user_id(state),
                "job_id": StateManager.get_job_id(state),
                "error_type": type(e).__name__,
            },
        )
