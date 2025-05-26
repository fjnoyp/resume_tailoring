"""
Info Collection Subgraph Nodes

Manages conversation flow for collecting missing resume information.
"""

import json
import logging
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.errors import GraphInterrupt

from src.main_agent import model
from src.tools.supabase_storage_tools import get_file_paths
from src.info_collection.update_user_full_resume import update_user_full_resume
from .state import InfoCollectionState

logging.basicConfig(level=logging.DEBUG)


async def conversation_starter(
    state: InfoCollectionState, config: RunnableConfig
) -> Dict[str, Any]:
    """
    Initializes the conversation by parsing requirements and asking first question.

    Args:
        state: Info collection state with missing_info_requirements
        config: LangChain runnable config

    Returns:
        Updated state with first question and remaining questions
    """
    try:
        missing_info_requirements = state["missing_info_requirements"]

        # Parse the missing info requirements (JSON from main graph)
        try:
            requirements = json.loads(missing_info_requirements)
            questions = requirements.get("questions_for_user", [])
            missing_info = requirements.get("missing_info", [])
        except json.JSONDecodeError:
            return {"error": "Invalid missing info requirements format"}

        if not questions:
            # No questions needed, mark as complete
            return {
                "is_complete": True,
                "final_collected_info": "No additional information needed",
            }

        # Start conversation with first question
        first_question = questions[0]
        remaining_questions = questions[1:]

        ai_message = AIMessage(
            content=f"""
I need to gather some additional information to better tailor your resume. Let me ask you a few questions:

**Question 1 of {len(questions)}:**
{first_question}

Please provide as much detail as possible about your relevant experience.
"""
        )

        return {
            "messages": [ai_message],
            "remaining_questions": remaining_questions,
            "collected_info": {"missing_info_categories": missing_info},
        }

    except Exception as e:
        logging.error(f"Error in conversation_starter: {e}")
        return {"error": f"Failed to start conversation: {str(e)}"}


async def question_asker(
    state: InfoCollectionState, config: RunnableConfig
) -> Dict[str, Any]:
    """
    Asks the next question or processes user response.

    Args:
        state: Current conversation state
        config: LangChain runnable config

    Returns:
        Updated state with next question or completion
    """
    try:
        messages = state["messages"]
        remaining_questions = state["remaining_questions"]
        collected_info = state["collected_info"]

        # Check if we have a user response to process
        if messages and isinstance(messages[-1], HumanMessage):
            # Process the user's response
            user_response = messages[-1].content

            # Store the response
            question_number = len(collected_info) - 1  # -1 for missing_info_categories
            collected_info[f"response_{question_number}"] = user_response

            # Check if we have more questions
            if remaining_questions:
                next_question = remaining_questions[0]
                remaining_questions = remaining_questions[1:]

                total_questions = len(collected_info) + len(remaining_questions)
                current_question_num = len(collected_info)

                ai_message = AIMessage(
                    content=f"""
Thank you for that information!

**Question {current_question_num} of {total_questions}:**
{next_question}

Please provide as much detail as possible.
"""
                )

                return {
                    "messages": [ai_message],
                    "remaining_questions": remaining_questions,
                    "collected_info": collected_info,
                }
            else:
                # No more questions, move to completion
                return {"collected_info": collected_info, "is_complete": True}
        else:
            # No user response yet, trigger interrupt to get user input
            raise GraphInterrupt("Waiting for user response")

    except GraphInterrupt:
        raise  # Re-raise GraphInterrupt
    except Exception as e:
        logging.error(f"Error in question_asker: {e}")
        return {"error": f"Failed to process question: {str(e)}"}


async def info_formatter(
    state: InfoCollectionState, config: RunnableConfig
) -> Dict[str, Any]:
    """
    Formats collected information and updates the full resume file.

    Args:
        state: State with collected information and current full_resume
        config: LangChain runnable config

    Returns:
        Final formatted information and updated full resume content
    """
    try:
        collected_info = state["collected_info"]
        user_id = state["user_id"]
        current_full_resume = state["full_resume"]

        # Format the collected information for immediate use
        format_prompt = f"""
You are a professional resume expert. Format the collected user responses into a structured summary that can be used for resume tailoring.

The user was asked questions to fill gaps in their resume. Here's what they provided:

COLLECTED_RESPONSES:
{json.dumps(collected_info, indent=2)}

Format this into a clear, structured summary that highlights:
- Key experiences and achievements mentioned
- Specific skills and technologies
- Quantifiable results and metrics
- Relevant projects or responsibilities

Output in markdown format for easy integration into resume tailoring.
"""

        response = await model.ainvoke(format_prompt, config=config)
        formatted_info = response.content

        # Update the full resume file with collected information
        file_paths = get_file_paths(user_id, "")  # Empty job_id for user files
        full_resume_path = file_paths.user_full_resume_path

        logging.info(f"[DEBUG] Updating full resume at: {full_resume_path}")

        # Use update_user_full_resume function with current content
        update_result = await update_user_full_resume(
            full_resume_path, current_full_resume, formatted_info
        )

        if update_result is None:
            logging.warning(
                "Failed to update full resume, but continuing with collected info"
            )
            updated_full_resume = current_full_resume  # Use current if update failed
        else:
            # Extract updated content from the returned tuple
            summary_message, updated_full_resume = update_result
            logging.info(f"[DEBUG] {summary_message}")
            logging.info(
                f"[DEBUG] Full resume updated successfully: {len(updated_full_resume)} chars"
            )

        return {
            "final_collected_info": formatted_info,
            "updated_full_resume": updated_full_resume,
            "is_complete": True,
        }

    except Exception as e:
        logging.error(f"Error in info_formatter: {e}")
        return {"error": f"Failed to format information: {str(e)}"}


def should_continue(state: InfoCollectionState) -> str:
    """
    Determines next step in conversation flow.

    Args:
        state: Current state

    Returns:
        Next node name or "END"
    """
    if state.get("error"):
        return "END"

    if state.get("is_complete"):
        if state.get("final_collected_info"):
            return "END"
        else:
            return "info_formatter"

    # Check if we've started the conversation
    if not state.get("messages"):
        return "conversation_starter"

    return "question_asker"
