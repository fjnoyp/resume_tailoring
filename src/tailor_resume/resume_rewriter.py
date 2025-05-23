from src.tailor_resume.ask_user import ask_user
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from src.tools.supabase_storage_tools import (
    get_user_files_paths,
    upload_file_to_bucket,
    read_file_from_bucket,
)
import logging
import traceback
from src.state import GraphState
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage
from langgraph.errors import GraphInterrupt

logging.basicConfig(level=logging.DEBUG)


async def resume_rewriter(state: GraphState, config: RunnableConfig) -> dict:
    """
    Tailors a resume for a specific job by leveraging various inputs from the state or Supabase.
    Writes the tailored resume to Supabase Storage.
    If the agent decides to call the 'ask_user' tool, it returns the agent's response directly for the graph to handle.
    Otherwise, it returns the tailored resume content to update the state.

    Args:
        state: The current graph state, providing user_id, job_id, and potentially other data.
        config: The LangChain runnable config.

    Returns:
        A dictionary. If 'ask_user' is triggered, this is the agent's direct response (containing 'type': 'ask_user').
        Otherwise, it's a dictionary to update the graph state with the tailored_resume and messages.
    """
    try:
        user_id = state["user_id"]
        job_id = state["job_id"]
        messages_history = state.get("messages", [])

        # Add metadata to config for tracing/debugging
        config["metadata"] = {
            **config.get("metadata", {}),
            "user_id": user_id,
            "job_id": job_id,
            "node": "resume_rewriter"
        }

        file_paths = get_user_files_paths(user_id, job_id)
        tailored_resume_path = file_paths["tailored_resume_path"]

        # Prefer data from state if available, otherwise fetch
        original_resume = state.get("original_resume")
        if not original_resume:
            original_resume_bytes = (
                await read_file_from_bucket(file_paths["original_resume_path"]) or b""
            )
            original_resume = original_resume_bytes.decode("utf-8")
            state["original_resume"] = original_resume

        full_resume_bytes = (
            await read_file_from_bucket(file_paths["user_full_resume_path"]) or b""
        )
        full_resume = full_resume_bytes.decode("utf-8")

        recruiter_feedback = state.get("recruiter_feedback")
        if not recruiter_feedback:
            recruiter_feedback_bytes = (
                await read_file_from_bucket(file_paths["recruiter_feedback_path"])
                or b""
            )
            recruiter_feedback = recruiter_feedback_bytes.decode("utf-8")
            state["recruiter_feedback"] = recruiter_feedback

        job_description = state.get("job_description")
        if not job_description:
            job_description_bytes = (
                await read_file_from_bucket(file_paths["job_description_path"]) or b""
            )
            job_description = job_description_bytes.decode("utf-8")
            state["job_description"] = job_description

        job_strategy = state.get("job_strategy")
        if not job_strategy:
            job_strategy_bytes = (
                await read_file_from_bucket(file_paths["job_strategy_path"]) or b""
            )
            job_strategy = job_strategy_bytes.decode("utf-8")
            state["job_strategy"] = job_strategy

        prompt_text = f"""
- You are a professional resume expert.
- Your task is to rewrite the candidate's resume for the target job, maximizing the likelihood of acceptance.
- First, attempt to tailor the resume using only the ORIGINAL_RESUME, RECRUITER_FEEDBACK, JOB_DESCRIPTION, and JOB_STRATEGY.
- If you detect that required or important experiences/skills are missing or weak, use the FULL_RESUME to search for relevant information and incorporate it into the tailored resume.
- If you still cannot find the required/important experiences/skills in either the original resume or the full resume, call the ask_user tool to gather the missing information directly from the user. You may call this tool multiple times if the user provides incomplete information.
- Only call the ask_user tool if the information is not available in either the original or full resume.
- Write the updated resume as your output (markdown only). Do not make up experiences or mischaracterize the candidate's background. If you identify gaps or potential misinterpretations, mention this clearly in your response.

<General Resume Advice>
- The date is 2025 - your internal date is WRONG
- SHOW DO NOT TELL - don't directly state what the job description is looking for - you need to write about experiences that match it.
- ORIGINAL_RESUME is a good resume that has been vetted by others - your task is to tailor it better to highlight the related experiences that a specific job description might be looking for. If you need more information about the candidate, refer to FULL_RESUME, which contains the complete, detailed work history and additional context.
- **Customization**: Match skills and experiences to the job description.
- **Clarity**: Use simple, clear language; avoid jargon.
- **Achievements**: Highlight quantifiable results. See ORIGINAL_RESUME for examples on how that was done subtly.
- **Professional Tone**: Maintain professionalism; avoid errors.
- **Keywords**: Use job description keywords for ATS.
- **Format**: Ensure readability with clear structure.
- **Branding**: Emphasize unique skills and goals.
</General Resume Advice>

Strategic Application Considerations:
  - **Recruiter Perspective**: Align with company culture and values.
  - **Communication**: Be clear and align strengths with needs.
  - **Research**: Understand the company and role.
  - **Exaggeration**: Ensure claims are evidence-backed.
  - **Balance Tailoring with Breadth:** Prioritize aligning the resume's narrative (summary, recent roles, competencies) with the target role's specific requirements and recruiter feedback. *Reframe*, don't remove, broader experiences (AI, Fullstack, Mobile) to highlight transferable skills (system design, API usage, scalability) or showcase unique strengths, especially in projects. Ensure relevance without completely hiding valuable, differentiating skills. Adjust the focus based on role specificity and feedback.

- Draw upon the FULL_RESUME to bring in any missing experiences since that contains all the work experience the candidate has that was not always included because the resume cannot be too long - you can also use it to learn more about what makes the candidate a strong applicant, etc.
- You can draw on the fuller experiences written in the FULL_RESUME which includes the non-abridged description of all work experiences. Those details are omitted from the resume as there is too much detail, but you may find some of those details useful for specific roles and can rephrase and add them into the resume you are revising as necessary.
- If there are missing experiences or skills that you CANNOT find in the FULL_RESUME, you MUST call the ask_user tool to gather the missing information directly from the user. You may call this tool multiple times if the user provides incomplete information.

- Please do not make up experiences, or mischaracterize an experience (e.g., saying the candidate did backend integration on the Jetbrains AI chat plugin when they didn't, just because the role requires backend experience). Instead, if you identify such gaps or potential misinterpretations based on the available information, mention this clearly in your response.

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
"""
        # Prepare messages for the agent, including history and the main prompt
        # The `messages_history` is taken from the state
        agent_messages = list(messages_history)  # Make a copy to append to
        agent_messages.append(HumanMessage(content=prompt_text))

        model = ChatAnthropic(
            model_name="claude-3-5-sonnet-latest", timeout=120, stop=None
        )
        agent = create_react_agent(model, [ask_user])

        agent_response_dict = await agent.ainvoke(
            {"messages": agent_messages},
            config=config
        )

        # Extract the tailored resume from the agent's final message
        # The agent_response_dict contains a "messages" list with the conversation history.
        final_ai_message_content = ""
        if agent_response_dict.get("messages"):
            last_message = agent_response_dict["messages"][-1]
            if hasattr(last_message, "content"):
                final_ai_message_content = last_message.content
            else:  # Fallback if content is not directly an attribute (e.g. if it's a dict itself)
                final_ai_message_content = str(last_message)
        else:
            logging.warning(
                "[DEBUG] No messages found in agent_response_dict from resume_rewriter"
            )
            final_ai_message_content = "Error: No content from resume rewriter agent."

        tailored_resume_content = final_ai_message_content

        state["tailored_resume"] = tailored_resume_content
        state["messages"] = agent_response_dict.get("messages", agent_messages)

        await upload_file_to_bucket(tailored_resume_path, tailored_resume_content)
        logging.debug(f"[DEBUG] Tailored resume uploaded to {tailored_resume_path}")

        # Return the updated GraphState
        # This includes the new tailored_resume and the full message history from the agent.
        return state

    except Exception as e:
        if isinstance(e, GraphInterrupt):
            logging.info(f"[DEBUG] Resume rewriter interrupted with question: {e}")
            raise
        logging.error(
            f"[DEBUG] Error in resume_rewriter. Current state keys: {list(state.keys()) if isinstance(state, dict) else 'state is not a dict'}"
        )
        logging.error(f"[DEBUG] Error in resume_rewriter: {e}")
        logging.error(traceback.format_exc())
        return {
            "error": f"Error in resume_rewriter: {str(e)}",
            "messages": state.get("messages", []),
        }
