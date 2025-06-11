"""
Cover Letter Generation Node

Generates a cover letter based on the tailored resume, job description, and recruiter feedback.
Uses the same structure and patterns as other processing nodes.
"""

import logging
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig

from src.llm_config import model
from src.graphs.cover_letter.state import CoverLetterState, set_error
from src.tools.state_data_manager import save_processing_result
from src.utils.node_utils import validate_fields, setup_metadata, handle_error

logging.basicConfig(level=logging.DEBUG)


async def cover_letter_generator(state: CoverLetterState, config: RunnableConfig) -> Dict[str, Any]:
    """
    Generate a cover letter based on the tailored resume and recruiter feedback.
    
    Input: tailored_resume, recruiter_feedback, job_description, full_resume (loaded by load_cover_letter_data)
    Output: cover_letter (generated cover letter content)
    
    Args:
        state: Cover letter state with required inputs loaded
        config: LangChain runnable config
        
    Returns:
        Dictionary with cover_letter or error state
    """
    try:
        # Validate required fields
        error_msg = validate_fields(
            state, ["tailored_resume", "recruiter_feedback", "job_description"], "cover letter generation"
        )
        if error_msg:
            return {"error": error_msg}

        # Extract fields using type-safe dot notation
        user_id = state.user_id
        job_id = state.job_id
        tailored_resume = state.tailored_resume
        recruiter_feedback = state.recruiter_feedback
        job_description = state.job_description
        full_resume = state.full_resume

        # Setup metadata
        setup_metadata(config, "cover_letter_generator", user_id, job_id)

        # Create the prompt using the analysis and generation logic from the original
        prompt = f"""
You are a professional cover letter writer. Generate a compelling cover letter that addresses the specific job requirements and recruiter concerns.

Your main goal is to create a cover letter that helps the candidate's overall application for the job. Focus on content that addresses recruiter concerns and highlights the candidate's strengths and fit for the role.

Key Analysis and Generation Guidelines:
- Consider the weaknesses highlighted in the recruiter feedback and how the cover letter can help support or explain any weaknesses indirectly to increase the chance the recruiter accepts the candidate's application.
- Consider the ideal strengths/general experience the candidate has that might not be fully explained in the resume or could be explained more that would help the overall chance for the recruiter to accept the application.
- You may want to add some extra details about the candidate included in the full resume that would help the application but are not present in the tailored resume.
- Overall, consider the psychology and goals of the recruiter and how they might assess the application and how this cover letter can help the candidate's overall application.
- Write for brevity (200-500 words max), show do not tell. Consider what makes an ideal cover letter and apply those principles to what you write.
- If possible make it unique in an appropriate way / creatively different that could help attract more attention.

---

**Job Description:**
{job_description}

---

**Tailored Resume:**
{tailored_resume}

---

**Recruiter Feedback:**
{recruiter_feedback}

---

**Full Resume:**
{full_resume}

---

Generate a professional cover letter that complements the resume and addresses the role requirements. Return ONLY the cover letter content.
"""

        # Generate cover letter using simple model call
        response = await model.ainvoke(prompt, config=config)
        cover_letter_content = response.content
        
        if not cover_letter_content:
            return set_error("Cover letter generation returned empty content")

        # Save cover letter to database using StateDataManager
        # TODO: Shouldn't we rename the field to "cover_letter"?
        await save_processing_result(user_id, job_id, "tailored_cv", cover_letter_content)

        logging.debug(f"[DEBUG] Generated cover letter: {len(cover_letter_content)} chars for {user_id}/{job_id}")
        
        return {
            "cover_letter": cover_letter_content
        }

    except Exception as e:
        return handle_error(e, "cover_letter_generator") 