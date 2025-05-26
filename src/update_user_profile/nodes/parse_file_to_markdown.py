from src.tools.supabase_storage_tools import read_file_from_bucket, get_user_files_paths
from src.tools.parse_pdf_tool import parse_pdf
from src.update_user_profile.state import FullResumeGraphState
from langchain_core.runnables import RunnableConfig
from ...main_agent import agent
import logging
import traceback

logging.basicConfig(level=logging.DEBUG)


async def parse_file_to_markdown(state: FullResumeGraphState, config: RunnableConfig) -> dict:
    """
    Extracts structured information from existing resume or related files in Supabase Storage and returns it as properly formatted markdown.
    Use this tool to convert files' content into markdown for further resume updates. Handles both PDF and text-based files.

    Input: input_data (with the file names separated by commas)
    Output: input_data (with the parsed file(s) content)

    Args:
        state: The current graph state.
        config: The LangChain runnable config.

    Returns:
        A dictionary containing the parsed files content in the input_data field, ready for the next node in the graph.
    """
    try:
        file_names = [name.strip() for name in state["input_data"].split(",")]
        user_id = state["user_id"]

        # Add metadata to config for tracing/debugging
        config["metadata"] = {
            **config.get("metadata", {}),
            "file_names": file_names,
            "user_id": user_id,
            "node": "parse_additional_file"
        }

        # Get the base path structure
        file_paths = get_user_files_paths(user_id)
        
        # Read all files content
        all_content = []
        for file_name in file_names:
            # Replace [file_name] with actual file name in the path template
            file_path = file_paths["other_files_path"].replace("[file_name]", file_name)
            file_content_bytes = await read_file_from_bucket(file_path) or b""
            
            # Handle PDF files differently
            if file_name.lower().endswith('.pdf'):
                file_content = await parse_pdf(file_content_bytes) or ""
            else:
                file_content = file_content_bytes.decode("utf-8")
                
            all_content.append(f"Content from {file_name}:\n{file_content}")

        combined_content = "\n\n---\n\n".join(all_content)

        messages = [
            {
                "role": "user",
                "content": f"""
- You are a professional resume parser tasked with extracting comprehensive career information
- Your goal is to convert the provided document(s) into a well-structured resume format
- Follow these strict guidelines:

1. CONTENT EXTRACTION:
   - Work experience with detailed responsibilities and achievements
   - Education history with degrees, institutions, and dates
   - Technical skills and certifications with proficiency levels
   - Projects and notable achievements
   - Professional summary and key qualifications
   - Relevant volunteer work or extracurricular activities

2. STRUCTURE:
   - Use clear markdown formatting throughout
   - Organize content into logical sections
   - Maintain chronological order in experience/education
   - Use consistent date formats
   - Preserve formatting for lists and bullet points

3. QUALITY CONTROL:
   - Maintain accurate job titles and company names
   - Preserve exact dates and durations
   - Keep professional language and tone
   - Remove any redundant information
   - Ensure consistent formatting across sections
   - Merge information from multiple sources without duplication

SOURCE CONTENT:
{combined_content}

Return ONLY the properly formatted markdown content. Do not include any explanations, comments, or other text before or after the markdown content.
""",
            }
        ]

        agent_response = await agent.ainvoke({"messages": messages})
        logging.debug(
            "[DEBUG] Agent response in parse_additional_file tool: %s",
            agent_response["messages"][-1:],
        )

        # Extract the markdown content from agent response
        parsed_content = agent_response["messages"][-1].content

        # Return updated state
        return {"input_data": parsed_content}

    except Exception as e:
        logging.error(f"[DEBUG] Error in parse_additional_file. Current state: {state}")
        logging.error(f"[DEBUG] Error in parse_additional_file tool: {e}")
        logging.error(traceback.format_exc())
        return {"error": f"Error in parse_additional_file: {str(e)}"}
