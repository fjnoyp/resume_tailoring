from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import logging
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from tools.resume_tailoring_tools import resume_tailoring_tools
from tools.user_experience_gathering_tools import user_experience_gathering_tools
import logging

# Initialize the model
model = ChatAnthropic(
    model_name="claude-3-7-sonnet-latest",
    timeout=120,
    stop=None
)

agent = create_react_agent(model, [*resume_tailoring_tools, *user_experience_gathering_tools])

logging.basicConfig(level=logging.DEBUG)

async def process_query(query: list, debug: bool = False):
    if debug:
        logging.debug("[DEBUG] process_query called with query: %s", query)

    agent_response = await agent.ainvoke({"messages": query})

    if debug:
        logging.debug("[DEBUG] agent_response: %s", agent_response)

    return agent_response['messages'][-1].content

MAX_HISTORY = 20  # or whatever fits your model's context window
