"""
Resume Screening Node

Evaluates resumes from a recruiter's perspective against job requirements.
Pure data processing - no file I/O.
"""

import logging
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from src.tools.supabase_storage_tools import (
    get_file_paths,
    upload_file_to_bucket,
)
from src.main_agent import agent
from src.state import GraphState, set_error

logging.basicConfig(level=logging.DEBUG)


async def resume_screener(state: GraphState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Screens resume from recruiter perspective against job requirements.

    Input: original_resume, job_description, job_strategy (all loaded by data_loader)
    Output: recruiter_feedback (analysis and recommendations)

    Args:
        state: Graph state with required inputs loaded
        config: LangChain runnable config

    Returns:
        Dictionary with recruiter_feedback or error state
    """
    try:
        user_id = state["user_id"]
        job_id = state["job_id"]
        original_resume = state["original_resume"]
        job_description = state["job_description"]
        job_strategy = state["job_strategy"]

        # Validate required inputs
        required_fields = {
            "original_resume": original_resume,
            "job_description": job_description,
            "job_strategy": job_strategy,
        }

        for field_name, field_value in required_fields.items():
            if not field_value:
                return set_error(f"{field_name} not available for screening")

        # Add metadata for tracing
        config["metadata"] = {
            **config.get("metadata", {}),
            "user_id": user_id,
            "job_id": job_id,
            "node": "resume_screener",
        }

        prompt = f"""
You are a professional recruiter evaluating candidates for a specific role.

Assess the resume below against the job description and strategic analysis. Consider that you have hundreds of candidates and need to be selective.

Provide a comprehensive markdown analysis with:
- Pros and cons of this candidate
- Clear reasoning for accept/reject recommendation
- Specific areas where candidate excels or falls short
- Well-reasoned justification for your decision

Be thorough and professional in your evaluation.

RESUME:
{original_resume}

JOB_DESCRIPTION:
{job_description}

STRATEGIC_ANALYSIS:
{job_strategy}
"""

        # Generate recruiter feedback
        response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": prompt}]}, config=config
        )

        recruiter_feedback = response["messages"][-1].content

        # Save to storage (only file I/O operation, isolated here)
        file_paths = get_file_paths(user_id, job_id)
        await upload_file_to_bucket(
            file_paths.recruiter_feedback_path, recruiter_feedback
        )

        logging.debug(
            f"[DEBUG] Recruiter feedback generated: {len(recruiter_feedback)} chars"
        )

        return {"recruiter_feedback": recruiter_feedback}

    except Exception as e:
        logging.error(f"[DEBUG] Error in resume_screener: {e}")
        return set_error(f"Resume screening failed: {str(e)}")
