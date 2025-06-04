"""
Resume Screening Node

Evaluates resumes from a recruiter's perspective against job requirements.
Pure data processing - no file I/O.
"""

import logging
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from src.llm_config import model
from src.graphs.resume_rewrite.state import GraphState, set_error
from src.tools.state_storage_manager import save_processing_result
from src.utils.node_utils import validate_fields, setup_metadata, handle_error

logging.basicConfig(level=logging.DEBUG)


async def resume_screener(state: GraphState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Screens resume from recruiter perspective against job requirements.

    Input: original_resume, job_description, company_strategy (all loaded by data_loader)
    Output: recruiter_feedback (analysis and recommendations)

    Args:
        state: Graph state with required inputs loaded
        config: LangChain runnable config

    Returns:
        Dictionary with recruiter_feedback or error state
    """
    try:
        # Validate required fields using dot notation
        error_msg = validate_fields(
            state, ["original_resume", "job_description", "company_strategy"], "screening"
        )
        if error_msg:
            return {"error": error_msg}

        # Extract fields using type-safe dot notation
        user_id = state.user_id
        job_id = state.job_id
        original_resume = state.original_resume
        job_description = state.job_description
        company_strategy = state.company_strategy

        # Setup metadata
        setup_metadata(config, "resume_screener", user_id, job_id)

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
{company_strategy}
"""

        # Generate recruiter feedback using simple model call
        response = await model.ainvoke(prompt, config=config)
        recruiter_feedback = response.content

        # Save to storage using StateStorageManager
        await save_processing_result(
            user_id, job_id, "recruiter_feedback", recruiter_feedback
        )

        logging.debug(
            f"[DEBUG] Recruiter feedback generated: {len(recruiter_feedback)} chars"
        )

        return {"recruiter_feedback": recruiter_feedback}

    except Exception as e:
        return handle_error(e, "resume_screener")
