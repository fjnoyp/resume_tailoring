"""
Info Collection Subgraph Nodes

Conversational agent flow for collecting missing resume information.
"""

import json
import logging
from typing import Dict, Any
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage
from langgraph.prebuilt import create_react_agent

from src.llm_config import model
from src.graphs.update_user_profile.graph import update_user_profile_graph
from src.graphs.update_user_profile.state import create_update_profile_state
from src.utils.node_utils import validate_fields, setup_metadata, handle_error
from .state import InfoCollectionState

logging.basicConfig(level=logging.DEBUG)


def create_conversation_agent():
    """
    Create a react agent for conversational info collection.

    Returns:
        Configured react agent for conversation
    """
    system_prompt = """You are a professional resume advisor helping collect missing information to improve a user's resume.

IMPORTANT: You will receive a system message at the start listing the specific missing information areas to collect.

Your role:
1. Focus on collecting information about the specific missing areas provided
2. Have a natural conversation with the user to gather these details
3. Ask follow-up questions to get specific achievements and quantifiable results
4. Keep mental notes of what information you've collected for each missing area
5. When you have sufficient information for all missing areas, say "CONVERSATION_COMPLETE"

Guidelines:
- Be conversational and encouraging
- Ask for specific examples, achievements, and metrics
- Focus on quantifiable results when possible
- Don't ask about all missing items at once - have a natural flow
- If the user doesn't have experience in an area, acknowledge it and move on
- End with "CONVERSATION_COMPLETE" when you've covered all missing areas
"""

    # Create react agent with no tools (just conversation)
    agent = create_react_agent(model, [], prompt=system_prompt)
    return agent


# Create the conversation agent instance
conversation_agent = create_conversation_agent()


async def conversation_starter(
    state: InfoCollectionState, config: RunnableConfig
) -> Dict[str, Any]:
    """
    Initializes the conversation by adding a system message about missing info.

    Args:
        state: Info collection state with missing_info list
        config: LangChain runnable config

    Returns:
        Updated state with initial system context
    """
    try:
        missing_info = state["missing_info"]

        if not missing_info:
            return {
                "conversation_complete": True,
                "final_collected_info": "No additional information needed",
            }

        # Setup metadata if user_id available
        user_id = state.get("user_id")
        if user_id:
            setup_metadata(
                config, "conversation_starter", user_id, graph="info_collection"
            )

        # Create detailed context message about missing information
        missing_info_text = "\n".join([f"- {item}" for item in missing_info])

        context_message = SystemMessage(
            content=f"""MISSING INFORMATION TO COLLECT:
{missing_info_text}

Please collect information about these specific areas from the user. Start with a friendly greeting and explain that you'd like to help strengthen their resume by gathering some additional information. Focus on these areas throughout the conversation."""
        )

        return {"messages": [context_message]}

    except Exception as e:
        return handle_error(e, "conversation_starter")


async def update_resume(
    state: InfoCollectionState, config: RunnableConfig
) -> Dict[str, Any]:
    """
    Termination node that creates targeted summary and calls update_user_profile graph.

    Args:
        state: State with conversation messages and user context
        config: LangChain runnable config

    Returns:
        Final state with formatted info and updated resume
    """
    try:
        # Validate required fields
        error_msg = validate_fields(
            state, ["user_id", "messages", "missing_info"], "update"
        )
        if error_msg:
            return {"error": error_msg}

        # Extract fields
        user_id = state["user_id"]
        messages = state["messages"]
        missing_info = state["missing_info"]

        # Setup metadata
        setup_metadata(config, "update_resume", user_id, graph="info_collection")

        # Extract full conversation (excluding system messages)
        conversation_parts = []
        for msg in messages[1:]:  # Skip the initial system message
            if hasattr(msg, "type"):
                role = "Assistant" if msg.type == "ai" else "User"
                conversation_parts.append(f"{role}: {msg.content}")

        if not conversation_parts:
            return {
                "final_collected_info": "No information collected",
                "updated_full_resume": state.get("full_resume", ""),
            }

        # Create targeted summary that maps collected info to missing areas
        conversation_text = "\n\n".join(conversation_parts)
        missing_info_list = "\n".join([f"- {item}" for item in missing_info])

        summary_prompt = f"""
You are a professional resume expert. Analyze this conversation where a user provided information to fill specific gaps in their resume.

MISSING INFORMATION AREAS THAT WERE TARGETED:
{missing_info_list}

CONVERSATION:
{conversation_text}

Create a structured summary that:
1. Maps the collected information to each missing area
2. Highlights specific achievements, metrics, and examples provided
3. Notes any areas where the user indicated they don't have relevant experience
4. Formats the information for easy integration into a resume

For each missing area, clearly indicate:
- What information was collected (if any)
- Specific details, achievements, or metrics mentioned
- If no relevant experience was provided

Output in clear markdown format with sections for each missing area.
"""

        response = await model.ainvoke(summary_prompt, config=config)
        formatted_info = response.content

        # Call the separate update_user_profile graph to handle resume updating
        logging.info(f"[DEBUG] Calling update_user_profile graph with targeted summary")

        update_state = create_update_profile_state(
            user_id=user_id, operation_mode="update_resume", input_data=formatted_info
        )

        # Call the update_user_profile graph
        update_result = await update_user_profile_graph.ainvoke(
            update_state, config=config
        )

        if update_result.get("error"):
            logging.warning(f"Failed to update full resume: {update_result['error']}")
            updated_full_resume = state.get(
                "full_resume", ""
            )  # Use current if update failed
        else:
            updated_full_resume = update_result.get(
                "updated_full_resume", state.get("full_resume", "")
            )
            logging.info(f"[DEBUG] Full resume updated by update_user_profile graph")

        return {
            "final_collected_info": formatted_info,
            "updated_full_resume": updated_full_resume,
        }

    except Exception as e:
        return handle_error(e, "update_resume")


def should_continue(state: InfoCollectionState) -> str:
    """
    Routing function to determine if conversation should continue or terminate.

    Args:
        state: Current conversation state

    Returns:
        Next node name
    """
    # Check if conversation should terminate
    if state.get("conversation_complete"):
        return "update_resume"

    # Check if agent said CONVERSATION_COMPLETE
    messages = state.get("messages", [])
    if messages:
        last_message = messages[-1]
        if (
            hasattr(last_message, "content")
            and "CONVERSATION_COMPLETE" in last_message.content
        ):
            return "update_resume"

    # Continue conversation
    return "conversation_agent"
