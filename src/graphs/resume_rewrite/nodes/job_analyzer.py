"""
Job Analysis Node

Analyzes job descriptions to extract hiring strategy and requirements.
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


async def job_analyzer(state: GraphState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Analyzes job posting to understand company hiring strategy and requirements.

    Input: job_description (loaded by data_loader)
    Output: company_strategy (strategic analysis and company insights)

    Args:
        state: Graph state containing job description
        config: LangChain runnable config

    Returns:
        Dictionary with company_strategy or error state
    """
    try:
        # Validate required fields using dot notation
        error_msg = validate_fields(state, ["job_description"], "job analysis")
        if error_msg:
            return {"error": error_msg}

        # Extract fields using type-safe dot notation
        user_id = state.user_id
        job_id = state.job_id
        job_description = state.job_description

        # Setup metadata
        setup_metadata(config, "job_analyzer", user_id, job_id)

        prompt = f"""
You are a strategic analyst helping someone understand a company's hiring priorities.

Analyze this job posting and provide a comprehensive strategic analysis:

1. **Company Culture & Values**: What values and culture does this company prioritize?

2. **Key Requirements**: What are the must-have vs nice-to-have qualifications?

3. **Success Metrics**: How does this company likely measure success in this role?

4. **Hiring Priorities**: What type of candidate are they really looking for beyond the obvious requirements?

5. **Decision Makers**: Who likely makes the hiring decision and what would impress them?

6. **Competitive Advantage**: What would make a candidate stand out for this specific role?

Provide actionable insights that help understand the company's hiring strategy.

JOB_DESCRIPTION:
{job_description}
"""

        # Generate company strategy using simple model call
        response = await model.ainvoke(prompt, config=config)
        company_strategy = response.content

        # Save to storage using StateStorageManager
        await save_processing_result(user_id, job_id, "company_strategy", company_strategy)

        logging.debug(f"[DEBUG] Company strategy generated: {len(company_strategy)} chars")

        return {"company_strategy": company_strategy}

    except Exception as e:
        return handle_error(e, "job_analyzer")
