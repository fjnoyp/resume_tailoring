from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

isTest = False

if isTest:
    # Using Groq for free, fast cloud inference (no local installation needed)
    from langchain_groq import ChatGroq

    import os
    # Initialize with Groq's free API - very fast and generous free tier
    model = ChatGroq(
        model="llama-3.1-8b-instant",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.1,
        timeout=120
    )
else:
    # Initialize the model
    model = ChatAnthropic(model_name="claude-3-7-sonnet-latest", timeout=120, stop=None)

agent = create_react_agent(model, [])
