from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import logging
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from tools.resume_tailoring_tools import resume_tailoring_tools
from tools.user_experience_gathering_tools import user_experience_gathering_tools
from tools.supabase_storage_tools import get_user_files_paths
import logging
from langchain.callbacks.base import AsyncCallbackHandler
import json

# Initialize the model
model = ChatAnthropic(
    model_name="claude-3-7-sonnet-latest",
    timeout=120,
    stop=None
)

agent = create_react_agent(
    model,
    [*resume_tailoring_tools, *user_experience_gathering_tools, get_user_files_paths]
)

logging.basicConfig(level=logging.DEBUG)

# --- Streaming Callback Handler ---
class StreamingCallbackHandler(AsyncCallbackHandler):
    def __init__(self, queue):
        self.queue = queue

    async def on_chain_start(self, serialized, inputs, **kwargs):
        await self.queue.put({"type": "system", "content": "Agent: Starting reasoning..."})

    async def on_agent_action(self, action, **kwargs):
        await self.queue.put({
            "type": "tool",
            "content": f"Calling tool: {action.tool} with input: {action.tool_input}"
        })

    async def on_tool_end(self, output, **kwargs):
        await self.queue.put({
            "type": "tool_result",
            "content": f"Tool result: {output}"
        })

    async def on_llm_new_token(self, token, **kwargs):
        await self.queue.put({
            "type": "ai",
            "content": token
        })

# --- Streaming version ---
async def process_query_stream(conversation):
    async for event in agent.astream_events({"messages": conversation}):
        event_type = event.get("event", "")
        data = event.get("data", {})

        if event_type == "on_chain_start":
            yield {"type": "system", "content": "Agent: Starting reasoning..."}
        elif event_type == "on_agent_action":
            tool = data.get("tool", "unknown tool")
            tool_input = data.get("tool_input", "")
            yield {"type": "tool", "content": f"Calling tool: {tool} with input: {tool_input}"}
        elif event_type == "on_tool_end":
            output = data.get("output", "")
            yield {"type": "tool_result", "content": f"Tool result: {output}"}
        elif event_type == "on_llm_new_token":
            token = data if isinstance(data, str) else str(data)
            yield {"type": "ai", "content": token}
        elif event_type == "on_chain_end":
            output = data.get("output", "")
            if output:
                yield {"type": "ai", "content": output}
        # If event is not a dict, yield as a system message
        elif not isinstance(event, dict):
            yield {"type": "system", "content": str(event)}


# --- Non-streaming version (unchanged) ---
async def process_query(query: list, debug: bool = False):
    if debug:
        logging.debug("[DEBUG] process_query called with query: %s", query)

    agent_response = await agent.ainvoke({"messages": query})

    if debug:
        logging.debug("[DEBUG] agent_response: %s", agent_response)

    return agent_response['messages'][-1].content

MAX_HISTORY = 20  # or whatever fits your model's context window

def to_serializable(obj):
    if hasattr(obj, "content"):
        return {"type": getattr(obj, "type", "system"), "content": getattr(obj, "content", str(obj))}
    if isinstance(obj, dict):
        return {k: to_serializable(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_serializable(x) for x in obj]
    return obj
