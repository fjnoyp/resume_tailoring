import logging
import traceback
from dataclasses import dataclass
from typing import Optional
from full_tailor_resume.update_user_profile import update_user_full_resume

logging.basicConfig(level=logging.DEBUG)

@dataclass
class AskUserRequest:
    user_id: str
    question: str
    context: Optional[str] = ""
    type: str = "ask_user"

async def ask_user(input: dict) -> AskUserRequest:
    """
    Requests user input by returning an AskUserRequest object.

    Args:
        question: The question to ask the user.
        context: (Optional) Additional context to help the user answer.
        user_id: The user's ID.

    Returns:
        An AskUserRequest instance to signal the orchestrator to prompt the user.
    """
    try:
        user_id = input.get("user_id", "")
        question = input["question"]
        context = input.get("context", "")
        return AskUserRequest(user_id=user_id, question=question, context=context)
    except Exception as e:
        logging.error(f"[DEBUG] Error in ask_user: {e}")
        logging.error(traceback.format_exc())
        raise
