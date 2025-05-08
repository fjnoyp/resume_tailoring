from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from fastapi import FastAPI, HTTPException
from langchain_anthropic import ChatAnthropic
import asyncio
from langgraph.prebuilt import create_react_agent
from tools.resume_tailoring_tools import resume_tailoring_tools
from tools.user_experience_gathering_tools import user_experience_gathering_tools

# Initialize the model
model = ChatAnthropic(
    model_name="claude-3-7-sonnet-latest",
    timeout=120,
    stop=None
)

agent = create_react_agent(model, [*resume_tailoring_tools, *user_experience_gathering_tools])

async def process_query(query: list, debug: bool = False):
    if debug:
        print("[DEBUG] process_query called with query:", query)

    agent_response = await agent.ainvoke({"messages": query})

    if debug:
        print("[DEBUG] agent_response:", agent_response)

    return agent_response['messages'][-1].content

MAX_HISTORY = 20  # or whatever fits your model's context window
