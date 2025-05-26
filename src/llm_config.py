from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent

# Initialize the model
model = ChatAnthropic(model_name="claude-3-7-sonnet-latest", timeout=120, stop=None)

agent = create_react_agent(model, [])
