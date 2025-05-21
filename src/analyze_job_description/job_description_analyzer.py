from src.tools.supabase_storage_tools import (
    get_user_files_paths,
    upload_file_to_bucket,
    read_file_from_bucket,
)
from ..main_agent import model
import logging
import traceback
from src.state import GraphState
from langchain_core.runnables import RunnableConfig

logging.basicConfig(level=logging.DEBUG)


async def job_description_analyzer(state: GraphState, config: RunnableConfig) -> dict:
    """
    Analyzes a job description to extract and synthesize the underlying company requirements, strategy, and recruiter psychology, producing a comprehensive markdown document.
    If job_description is not provided from state, it is loaded from Supabase Storage using user_id and job_id from state.

    Args:
        state: The current graph state.
        config: The LangChain runnable config.

    Returns:
        A dictionary to update the graph state with the job_strategy.
    """
    try:
        user_id = state["user_id"]
        job_id = state["job_id"]
        job_description = state.get("job_description")

        if not job_description:
            file_paths = get_user_files_paths(user_id, job_id)
            job_description_path = file_paths["job_description_path"]
            job_description_bytes = (
                await read_file_from_bucket(job_description_path) or b""
            )
            job_description = job_description_bytes.decode("utf-8")

        message = f"""
- You are an expert in recruitment strategy and organizational psychology.
- You have been given a job description for a company/role.
- Your task is to deeply analyze the job description and extract the underlying company requirements, expectations, and strategic priorities.
- Go beyond the surface: infer the psychology, motivations, and priorities of the company and its recruiters based on the language, structure, and focus of the job description.
- Synthesize your findings into a clear, well-structured markdown document called the Job Strategy Document.
- The document should include:
    - A summary of the company's core requirements and expectations for the role
    - Insights into the company's culture, values, and what they are truly seeking in a candidate
    - The likely priorities and pain points of the recruiters and hiring managers
    - Any implicit or unwritten requirements you can infer
    - Recommendations for how a candidate could best align themselves with this company's needs
- Only output markdown.

JOB_DESCRIPTION:
{job_description}
"""
        # Generate the job strategy document
        agent_response = await model.ainvoke(message)
        markdown_content = agent_response.content

        # Upload the job strategy document to the user's job directory in Supabase
        job_strategy_path = get_user_files_paths(user_id, job_id)["job_strategy_path"]
        await upload_file_to_bucket(job_strategy_path, markdown_content)
        logging.debug(f"[DEBUG] Job strategy document uploaded to {job_strategy_path}")

        # Return only the fields that update the state
        return {"job_strategy": markdown_content}
    except Exception as e:
        logging.error(f"[DEBUG] Error in analyze_job_description tool: {e}")
        logging.error(traceback.format_exc())
        # It's better to raise the exception or return a state that indicates an error
        # For now, returning a dict with an error message to fit the expected dict return type.
        return {"error": f"Error in job_description_analyzer: {str(e)}"}
