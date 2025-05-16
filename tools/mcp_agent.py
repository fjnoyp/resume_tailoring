import logging
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
from langchain_mcp_adapters.tools import load_mcp_tools
import asyncio
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from contextlib import AsyncExitStack
import os

# Using fetch mcp server to fetch LinkedIn data does not work because we need authentication
# Server parameters for HorizonDataWave LinkedIn MCP server
# Make sure to set these environment variables in your system or .env file
linkedin_server_params = StdioServerParameters(
    command="npx",
    args=["-y", "@horizondatawave/mcp"],
    env={
        "HDW_ACCESS_TOKEN": os.getenv("HDW_ACCESS_TOKEN"),
        "HDW_ACCOUNT_ID": os.getenv("HDW_ACCOUNT_ID")
    }
)

# add other server parameters as needed

async def invoke_mcp_agent(messages: list[dict[str, str]], server_params_list: list, additional_tools: list = []):
    """
    Invokes an agent with tools loaded from multiple MCP servers.
    Keeps all sessions open for the duration of the agent call.
    """
    all_tools = []
    all_tools.extend(additional_tools)
    model = ChatAnthropic(
        model_name="claude-3-5-sonnet-latest",
        timeout=120,
        stop=None
    )

    async with AsyncExitStack() as stack:
        sessions = []
        for params in server_params_list:
            client = await stack.enter_async_context(stdio_client(params))
            session = await stack.enter_async_context(ClientSession(*client))
            await asyncio.wait_for(session.initialize(), timeout=30)
            tools = await asyncio.wait_for(load_mcp_tools(session), timeout=30)
            logging.debug(f"Loaded tools: {tools}")
            all_tools.extend(tools)
            sessions.append(session)  # Keep reference if needed

        agent = create_react_agent(model, all_tools)
        result = await agent.ainvoke({"messages": messages})
        return result
