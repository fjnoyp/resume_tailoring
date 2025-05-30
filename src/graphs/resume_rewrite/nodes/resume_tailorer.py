"""
Resume Tailoring Node

Tailors resumes to specific jobs using analysis results and user interaction.
Tracks missing information persistently to reduce hallucinations and support iterative improvements.
"""

import logging
from typing import Dict, Any, List
from langchain_core.runnables import RunnableConfig
from pydantic import BaseModel, Field

from src.llm_config import model
from src.graphs.resume_rewrite.state import GraphState, set_error
from src.tools.state_storage_manager import save_processing_result
from src.utils.node_utils import validate_fields, setup_metadata, handle_error
from langgraph.types import interrupt
from langgraph.errors import GraphInterrupt

logging.basicConfig(level=logging.DEBUG)


class ResumeAnalysisAndGeneration(BaseModel):
    """Structured output for resume analysis and generation"""

    missing_info: List[str] = Field(
        description="List of specific missing information/experiences that would significantly improve the application"
    )
    tailored_resume: str = Field(description="The tailored resume in markdown format")


class InterruptData(BaseModel):
    """Typed data sent to client when missing info is detected"""

    missing_info: List[str] = Field(description="List of specific missing information")
    tailored_resume: str = Field(
        description="Current tailored resume generated with available info"
    )
    user_id: str = Field(description="User identifier for context")
    job_id: str = Field(description="Job identifier for context")
    full_resume: str = Field(description="Full resume for info collection context")


class InfoCollectionResult(BaseModel):
    """Expected result when resuming after info collection"""

    final_collected_info: str = Field(
        default="", description="Additional info collected from user"
    )
    updated_full_resume: str = Field(description="Updated full resume with new info")


async def resume_tailorer(state: GraphState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Tailors resume for specific job using analysis results with persistent missing info tracking.

    Input: original_resume, full_resume, job_description, job_strategy, recruiter_feedback
    Output: tailored_resume, missing_info (persistent context)

    Approach:
    1. Single AI call that analyzes missing info AND generates resume
    2. If missing_info found → interrupt with current resume + missing info
    3. On resume → restart entire node from top with new info
    4. Always produces resume output regardless of gaps

    Args:
        state: Graph state with all analysis results and data loaded
        config: LangChain runnable config

    Returns:
        Dictionary with tailored_resume and updated missing_info
    """
    try:
        # Validate required fields using dot notation
        required = [
            "original_resume",
            "full_resume",
            "job_description",
            "job_strategy",
            "recruiter_feedback",
        ]
        error_msg = validate_fields(state, required, "tailoring")
        if error_msg:
            return {"error": error_msg}

        # Extract fields using type-safe dot notation
        user_id = state.user_id
        job_id = state.job_id
        original_resume = state.original_resume
        full_resume = state.full_resume
        job_description = state.job_description
        job_strategy = state.job_strategy
        recruiter_feedback = state.recruiter_feedback

        # Setup metadata
        setup_metadata(config, "resume_tailorer", user_id, job_id)

        # Initialize with current full resume
        additional_info = ""
        working_full_resume = full_resume

        # Single AI call: Analyze missing info AND generate tailored resume
        prompt = f"""
You are a professional resume expert. Your task is to:
1. Identify what critical information is missing for optimal job tailoring
2. Generate the best possible tailored resume using available information

Be conservative with missing info - only flag things that would significantly impact application success.

For missing info analysis, consider:
- Missing relevant skills/technologies mentioned in job
- Lack of quantifiable achievements matching requirements
- Missing industry experience or certifications
- Absence of required leadership/project examples

For resume generation:
- SHOW DON'T TELL: Write about experiences matching job requirements
- Use quantifiable achievements and evidence-backed claims
- Include job description keywords for ATS optimization
- Never fabricate experiences or mischaracterize background
- DO NOT invent information to fill gaps - work with what you have
- Focus on strongest available experiences if missing critical info

RECRUITER_FEEDBACK:
{recruiter_feedback}

ORIGINAL_RESUME:
{original_resume}

FULL_RESUME:
{working_full_resume}

ADDITIONAL_COLLECTED_INFO:
{additional_info}

JOB_DESCRIPTION:
{job_description}

JOB_STRATEGY:
{job_strategy}

Return both the missing info analysis and the tailored resume.
"""

        # Use structured output for reliable parsing
        model_with_structure = model.with_structured_output(ResumeAnalysisAndGeneration)
        result = await model_with_structure.ainvoke(prompt, config=config)

        logging.debug(
            f"[DEBUG] Generated resume with {len(result.missing_info)} missing items identified"
        )

        # If we have missing info, interrupt to let client decide whether to collect more info
        if result.missing_info:
            logging.info(
                f"[DEBUG] Missing critical info detected, interrupting: {result.missing_info}"
            )

            # Prepare typed interrupt data for client
            interrupt_data = InterruptData(
                missing_info=result.missing_info,
                tailored_resume=result.tailored_resume,
                user_id=user_id,
                job_id=job_id,
                full_resume=working_full_resume,
            )

            # Interrupt execution - when resumed, interrupt() returns the collection result
            collection_result = interrupt(interrupt_data.model_dump())

            # If we get here, client has resumed with info collection result
            if collection_result:
                logging.info("[DEBUG] Resuming with collection result")
                try:
                    validated_result = InfoCollectionResult.model_validate(
                        collection_result
                    )
                    additional_info = validated_result.final_collected_info
                    working_full_resume = validated_result.updated_full_resume

                    logging.info(
                        f"[DEBUG] Restarting with collected info: {len(additional_info)} chars"
                    )

                    # Restart the AI call with new information
                    updated_prompt = prompt.replace(
                        full_resume, working_full_resume
                    ).replace(
                        f"ADDITIONAL_COLLECTED_INFO:\n{additional_info}",
                        f"ADDITIONAL_COLLECTED_INFO:\n{additional_info}",
                    )

                    result = await model_with_structure.ainvoke(
                        updated_prompt, config=config
                    )
                    logging.debug(
                        f"[DEBUG] Regenerated resume with {len(result.missing_info)} remaining missing items"
                    )

                except Exception as e:
                    logging.warning(
                        f"[DEBUG] Invalid collection result: {e}, using original resume"
                    )
            else:
                logging.info(
                    "[DEBUG] No collection result provided, using original resume"
                )

        # Save generated resume to storage
        await save_processing_result(
            user_id, job_id, "tailored_resume", result.tailored_resume
        )

        logging.debug(
            f"[DEBUG] Tailored resume completed: {len(result.tailored_resume)} chars"
        )

        return {
            "tailored_resume": result.tailored_resume,
            "missing_info": (
                "\n".join(result.missing_info) if result.missing_info else ""
            ),
        }
    except GraphInterrupt:
        raise
    except Exception as e:
        return handle_error(e, "resume_tailorer")
