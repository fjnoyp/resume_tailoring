"""
Job Analysis Node

Analyzes job descriptions to extract company strategy, requirements, and hiring psychology.
Pure data processing - no file I/O.
"""

import logging
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from src.main_agent import model
from src.state import GraphState, set_error
from src.tools.state_storage_manager import save_processing_result

logging.basicConfig(level=logging.DEBUG)


async def job_analyzer(state: GraphState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Analyzes job description to extract company strategy and requirements.

    Input: job_description (loaded by data_loader)
    Output: job_strategy (strategic analysis document)

    Args:
        state: Graph state with job_description loaded
        config: LangChain runnable config

    Returns:
        Dictionary with job_strategy or error state
    """
    try:
        user_id = state["user_id"]
        job_id = state["job_id"]
        job_description = state["job_description"]

        if not job_description:
            return set_error("Job description not available for analysis")

        # Add metadata for tracing
        config["metadata"] = {
            **config.get("metadata", {}),
            "user_id": user_id,
            "job_id": job_id,
            "node": "job_analyzer",
        }

        prompt = f"""
You are an expert in recruitment strategy and organizational psychology.

Analyze the job description below and extract the underlying company requirements, strategy, and recruiter psychology. Go beyond the surface to infer the psychology, motivations, and priorities of the company and its recruiters.

Create a strategic analysis document that includes:
- Company's core requirements and expectations for the role
- Insights into company culture, values, and what they truly seek in candidates
- Likely priorities and pain points of recruiters and hiring managers  
- Implicit or unwritten requirements you can infer
- Recommendations for how candidates can best align with company needs

Output only markdown.

JOB_DESCRIPTION:
{job_description}
"""

        # Generate analysis
        response = await model.ainvoke(prompt, config=config)
        job_strategy = response.content

        # Save to storage using StateStorageManager
        await save_processing_result(user_id, job_id, "job_strategy", job_strategy)

        logging.debug(f"[DEBUG] Job strategy generated: {len(job_strategy)} chars")

        return {"job_strategy": job_strategy}

    except Exception as e:
        logging.error(f"[DEBUG] Error in job_analyzer: {e}")
        return set_error(f"Job analysis failed: {str(e)}")
