"""
Info Collection Nodes

Conversational nodes for collecting missing resume information from users.
"""

import logging
import json
from typing import Dict, Any, List
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import AIMessage, HumanMessage

from src.llm_config import model
from src.graphs.info_collection.state import InfoCollectionState
from src.utils.node_utils import validate_fields, setup_profile_metadata, handle_error
from src.tools.state_data_manager import StateDataManager

logging.basicConfig(level=logging.DEBUG)


def is_user_message(msg):
    """Helper function to check if message is from user"""
    if isinstance(msg, HumanMessage):
        return True
    elif isinstance(msg, dict):
        return msg.get('type') == 'human'
    return msg.type == "human" if hasattr(msg, 'type') else False


async def info_collector_agent(
    state: InfoCollectionState, config: RunnableConfig
) -> Dict[str, Any]:
    """
    Conversational agent that collects missing resume information.

    Input: missing_info, messages (conversation history)
    Output: messages (updated conversation), final_collected_info (when complete)

    Args:
        state: InfoCollectionState with missing info requirements
        config: LangChain runnable config

    Returns:
        Dictionary with conversation updates or completion state
    """
    try:
        # Validate required fields using dot notation
        error_msg = validate_fields(
            state, ["missing_info", "user_id", "job_id"], "info collection"
        )
        if error_msg:
            return {"error": error_msg}

        # Extract fields using type-safe dot notation
        user_id = state.user_id
        job_id = state.job_id
        missing_info = state.missing_info
        messages = state.messages

        # Setup metadata
        setup_profile_metadata(config, "info_collector_agent", user_id)

        # Check if conversation should be terminated
        if state.conversation_complete:
            return {}  # No updates needed

        # Determine conversation phase
        if not messages:
            # Start conversation - introduce purpose
            missing_info_text = (
                ", ".join(missing_info)
                if missing_info
                else "additional resume information"
            )

            response_text = f"""Hi! I'm here to help gather some missing information for your resume.

I need to collect the following:
{missing_info_text}

Let's start with the first item. Can you tell me about: {missing_info[0] if missing_info else "your experience"}?"""

            ai_message = AIMessage(content=response_text)

            # Save AI message to database
            await StateDataManager.save_chat_message(
                job_id=job_id,
                content=response_text,
                role="ai"
            )
            logging.debug(f"[InfoCollector] Saved AI intro message to database for job {job_id}")

            return {"messages": [ai_message]}

        # Continue conversation - analyze last user message
        last_message = messages[-1]

        # Only process termination signals from user messages
        if is_user_message(last_message) and any(
            phrase in last_message.content.lower()
            for phrase in ["done", "finished", "that's all", "complete"]
        ):
            # Wrap up conversation
            collected_info = await _extract_collected_info(messages, missing_info)

            farewell_text = "Thank you! I've collected all the information. Your resume will be updated shortly."
            ai_message = AIMessage(content=farewell_text)

            # Save AI farewell message to database
            await StateDataManager.save_chat_message(
                job_id=job_id,
                content=farewell_text,
                role="ai",
                metadata={"conversation_complete": True, "collected_info_length": len(collected_info)}
            )
            logging.debug(f"[InfoCollector] Saved AI farewell message to database for job {job_id}")

            return {
                "messages": [ai_message],
                "final_collected_info": collected_info,
                "conversation_complete": True,
            }

        # # Only generate response if last message is from user (maintain proper conversation flow)
        # if not is_user_message(last_message):
        #     return {}  # Wait for user input

        # Generate contextual response
        context_prompt = f"""
You are a helpful assistant collecting missing resume information. You need to gather:
{', '.join(missing_info)}

Based on the conversation so far, ask relevant follow-up questions to collect the missing information.
Be conversational and helpful. If the user has provided some information, acknowledge it and ask for the next piece.

Keep responses brief and focused on collecting the specific information needed.
"""

        # Add context to messages for model
        context_messages = [{"role": "system", "content": context_prompt}] + [
            {"role": msg.type, "content": msg.content} for msg in messages
        ]

        response = await model.ainvoke(context_messages, config=config)
        ai_message = AIMessage(content=response.content)

        # Save AI response message to database
        await StateDataManager.save_chat_message(
            job_id=job_id,
            content=response.content,
            role="ai",
            metadata={"missing_info_remaining": missing_info}
        )
        logging.debug(f"[InfoCollector] Saved AI response message to database for job {job_id}")

        return {"messages": [ai_message]}

    except Exception as e:
        return handle_error(e, "info_collector_agent")


async def update_resume_with_collected_info(
    state: InfoCollectionState, config: RunnableConfig
) -> Dict[str, Any]:
    """
    Updates full resume with collected information.

    Input: final_collected_info, full_resume
    Output: updated_full_resume

    Args:
        state: InfoCollectionState with collected info and current resume
        config: LangChain runnable config

    Returns:
        Dictionary with updated_full_resume or error state
    """
    try:
        # Validate required fields using dot notation
        error_msg = validate_fields(
            state, ["final_collected_info", "full_resume"], "resume update"
        )
        if error_msg:
            return {"error": error_msg}

        # Extract fields using type-safe dot notation
        user_id = state.user_id
        collected_info = state.final_collected_info
        current_resume = state.full_resume

        # Setup metadata
        setup_profile_metadata(config, "update_resume_with_collected_info", user_id)

        prompt = f"""
Update this resume by incorporating the newly collected information.

INSTRUCTIONS:
1. Integrate the new information into the appropriate sections
2. Maintain the existing structure and formatting
3. Avoid duplication - merge similar information intelligently
4. Preserve all existing good content
5. Ensure consistency in style and tone

CURRENT RESUME:
{current_resume}

NEWLY COLLECTED INFORMATION:
{collected_info}

Return the complete updated resume.
"""

        response = await model.ainvoke(prompt, config=config)
        updated_resume = response.content

        logging.debug(
            f"[DEBUG] Resume updated with collected info: {len(updated_resume)} chars"
        )

        return {"updated_full_resume": updated_resume}

    except Exception as e:
        return handle_error(e, "update_resume_with_collected_info")


async def _extract_collected_info(messages: List, missing_info: List[str]) -> str:
    """
    Helper function to extract collected information from conversation messages.

    Args:
        messages: Conversation message history
        missing_info: List of information that was supposed to be collected

    Returns:
        Formatted string with collected information
    """
    # Extract user messages (excluding the first AI introduction)
    user_messages = [msg.content for msg in messages if msg.type == "human"]

    if not user_messages:
        return "No information collected"

    # Simple extraction - in practice you might want more sophisticated parsing
    collected_info = {
        "requested_info": missing_info,
        "user_responses": user_messages,
        "summary": " ".join(user_messages),
    }

    return json.dumps(collected_info, indent=2)
