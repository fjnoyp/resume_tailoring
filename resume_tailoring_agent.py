from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
import asyncio
from langgraph.prebuilt import create_react_agent
from resume_tailoring_tools import resume_tailoring_tools
import os

# Load environment variables
load_dotenv()

# Initialize the model
model = ChatAnthropic(
    model_name="claude-3-7-sonnet-latest",
    timeout=120,
    stop=None
)

# It's working properly without directly using the prompt here,
# it's now being used in the tools where the mdc file was referencing it
# 
# prompt = ChatPromptTemplate.from_messages([
#     ("system", GENERAL_RESUME_ADVICE_PROMPT)
# ])

async def process_query(query: str):
    print("[DEBUG] process_query called with query:", query)
    agent = create_react_agent(model, resume_tailoring_tools)
    agent_response = await agent.ainvoke({"messages": query})
    return agent_response

async def main():
    """Run example operation"""
    print("[DEBUG] main() called")

    result = await process_query(f"""Can you help me enhance my resume and write a cover letter for this job?

Job Description:
{os.getcwd().replace("\\", "/")}/samples/job-description.md

Resume:
{os.getcwd().replace("\\", "/")}/samples/resume.md

Full Resume:
{os.getcwd().replace("\\", "/")}/samples/linkedin-profile.md
""")
    print("\nAI response:", result)

if __name__ == "__main__":
    asyncio.run(main()) 