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
    Formats collected information for return to main graph.

    Args:
        state: State with collected information
        config: LangChain runnable config

    Returns:
        Final formatted information
    """
    try:
        collected_info = state["collected_info"]

        # Format the collected information
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

        return {"final_collected_info": formatted_info, "is_complete": True}

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
