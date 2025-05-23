import logging
import traceback
from langgraph.types import interrupt

logging.basicConfig(level=logging.DEBUG)

# TODO: add context to the input, and dd the provided info to the user's full resume
async def ask_user(input: dict) -> str:
    """
    Requests user input and returns the user's response.

    Args:
        question: The question to ask the user.

    Returns:
        The user's response as a string.
    """
    try:
        question = input["question"]
        return interrupt(question)
    except Exception as e:
        logging.error(f"[DEBUG] Error in ask_user: {e}")
        logging.error(traceback.format_exc())
        raise