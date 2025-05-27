"""
Resume Tailoring Node

Tailors resumes to specific jobs using analysis results and user interaction.
Pure data processing with optional info collection - no file I/O.
"""

import json
import logging
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from src.llm_config import model
from src.graphs.resume_rewrite.state import GraphState, set_error
from src.tools.state_storage_manager import save_processing_result
from src.graphs.info_collection.graph import info_collection_graph
from src.graphs.info_collection.state import create_info_collection_state
from langgraph.errors import GraphInterrupt

logging.basicConfig(level=logging.DEBUG)


async def resume_tailorer(state: GraphState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Tailors resume for specific job using analysis results.

    Input: original_resume, full_resume, job_description, job_strategy, recruiter_feedback (all loaded by data_loader)
    Output: tailored_resume

    If missing critical information, calls info collection subgraph to gather details from user.

    Args:
        state: Graph state with all analysis results and data loaded
        config: LangChain runnable config

    Returns:
        Dictionary with tailored_resume or error state
    """
    try:
        user_id = state["user_id"]
        job_id = state["job_id"]
        original_resume = state["original_resume"]
        full_resume = state["full_resume"]
        job_description = state["job_description"]
        job_strategy = state["job_strategy"]
        recruiter_feedback = state["recruiter_feedback"]

        # Validate required inputs
        required_fields = {
            "original_resume": original_resume,
            "full_resume": full_resume,
            "job_description": job_description,
            "job_strategy": job_strategy,
            "recruiter_feedback": recruiter_feedback,
        }

        for field_name, field_value in required_fields.items():
            if not field_value:
                return set_error(f"{field_name} not available for resume tailoring")

        # Add metadata for tracing
        config["metadata"] = {
            **config.get("metadata", {}),
            "user_id": user_id,
            "job_id": job_id,
            "node": "resume_tailorer",
        }

        # First, analyze what information might be missing
        analysis_prompt = f"""
You are a professional resume expert. Analyze the provided materials to identify what critical information might be missing for optimal job tailoring.

Review the ORIGINAL_RESUME and FULL_RESUME against the JOB_REQUIREMENTS and RECRUITER_FEEDBACK to identify gaps.

Output a JSON object with:
- "missing_info": list of specific missing information/experiences needed
- "has_sufficient_info": boolean indicating if current resume info is sufficient
- "questions_for_user": list of specific questions to ask user if information is missing

If has_sufficient_info is true, return empty lists for missing_info and questions_for_user.

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

Output ONLY the valid JSON content. Do not include any other text or ```json``` tags.
"""

        # Analyze missing information
        analysis_response = await model.ainvoke(analysis_prompt, config=config)

        # Parse analysis response
        try:
            analysis_data = json.loads(analysis_response.content)
            has_sufficient_info = analysis_data.get("has_sufficient_info", True)
            questions_for_user = analysis_data.get("questions_for_user", [])
        except json.JSONDecodeError:
            logging.warning(
                "Failed to parse analysis response, proceeding with available info"
            )
            has_sufficient_info = True
            questions_for_user = []

        # Collect additional information if needed
        additional_info = ""
        updated_full_resume = full_resume  # Start with current full resume

        if not has_sufficient_info and questions_for_user:
            logging.info(
                f"[DEBUG] Collecting additional info via subgraph: {len(questions_for_user)} questions"
            )

            try:
                # Create subgraph state with full resume context
                subgraph_state = create_info_collection_state(
                    missing_info_requirements=analysis_response.content,
                    user_id=user_id,
                    full_resume=full_resume,  # Pass full resume for context-aware questioning
                )

                # Call info collection subgraph
                # Note: Not passing config to avoid serialization issues with subgraph calls
                logging.info(f"[DEBUG] About to call info_collection_graph.ainvoke...")
                collection_result = await info_collection_graph.ainvoke(
                    subgraph_state #, config=config
                )
                additional_info = collection_result.get("final_collected_info", "")
                updated_full_resume = collection_result.get(
                    "updated_full_resume", full_resume
                )

                logging.debug(
                    f"[DEBUG] Additional info collected: {len(additional_info)} chars"
                )
                if updated_full_resume != full_resume:
                    logging.debug(
                        f"[DEBUG] Full resume updated: {len(updated_full_resume)} chars"
                    )
            except GraphInterrupt:
                raise  # Re-raise GraphInterrupt
            except Exception as subgraph_error:
                logging.warning(
                    f"[DEBUG] Info collection subgraph failed: {subgraph_error}, proceeding with available info"
                )
                # Continue with available information if subgraph fails
                additional_info = ""
                updated_full_resume = full_resume

        # Generate tailored resume with all available information
        tailoring_prompt = f"""
You are a professional resume expert specializing in job-specific tailoring.

Tailor the candidate's resume for maximum acceptance likelihood using all available information:

Guidelines:
- SHOW DON'T TELL: Write about experiences that match job requirements
- Use quantifiable achievements and evidence-backed claims
- Maintain professional tone and clear structure
- Include job description keywords for ATS
- Never fabricate experiences or mischaracterize background
- Integrate additional information naturally into relevant sections

Output the tailored resume in markdown format.

RECRUITER_FEEDBACK:
{recruiter_feedback}

ORIGINAL_RESUME:
{original_resume}

FULL_RESUME:
{updated_full_resume}

ADDITIONAL_COLLECTED_INFO:
{additional_info}

JOB_DESCRIPTION:
{job_description}

JOB_STRATEGY:
{job_strategy}
"""

        # Generate tailored resume
        response = await model.ainvoke(tailoring_prompt, config=config)
        tailored_resume = response.content

        # Save to storage using StateStorageManager
        await save_processing_result(
            user_id, job_id, "tailored_resume", tailored_resume
        )

        logging.debug(
            f"[DEBUG] Tailored resume generated: {len(tailored_resume)} chars"
        )

        return {"tailored_resume": tailored_resume}

    except GraphInterrupt:
        raise  # Re-raise GraphInterrupt
    except Exception as e:
        logging.error(f"[DEBUG] Error in resume_tailorer: {e}")
        return set_error(f"Resume tailoring failed: {str(e)}")
