from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp import ClientSession
from langchain_mcp_adapters.tools import load_mcp_tools
import traceback
import asyncio
import os
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic

# Server parameters for server-filesystem
filesystem_server_params = StdioServerParameters(
    command="npx",
    args=[
          "-y",
          "@modelcontextprotocol/server-filesystem",
          f"{os.getcwd()}"
        ],
)

model = ChatAnthropic(
    model_name="claude-3-5-sonnet-latest",
    timeout=120,
    stop=None
)

# We should figure out a way to not have to load the tools every time
# but currently this is the only way I could get the tools to work properly
async def invoke_filesystem_mcp_agent(message: str):
    global filesystem_mcp_session
    async with stdio_client(filesystem_server_params) as (read, write):
        async with ClientSession(read, write) as session:
            try:
                await asyncio.wait_for(session.initialize(), timeout=30)
            except Exception as e:
                print(f"[ERROR] Exception during session.initialize(): {e}")
                traceback.print_exc()
                return
            try:
                print("[DEBUG] Loading MCP tools...")
                filesystem_mcp_tools = await asyncio.wait_for(load_mcp_tools(session), timeout=30)
                print(f"[DEBUG] Loaded {len(filesystem_mcp_tools)} MCP tools in load_filesystem_mcp_tools")
            except Exception as e:
                print(f"[ERROR] Exception during load_mcp_tools: {e}")
                traceback.print_exc()
                return

            agent = create_react_agent(model, filesystem_mcp_tools)
            result = await agent.ainvoke({"messages": message})
            return result
