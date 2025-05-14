from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import logging
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from tools.resume_tailoring_tools import resume_tailoring_tools
from tools.user_experience_gathering_tools import user_experience_gathering_tools
from tools.supabase_storage_tools import get_user_files_paths, list_files_in_bucket
import logging

# Initialize the model
model = ChatAnthropic(
    model_name="claude-3-7-sonnet-latest",
    timeout=120,
    stop=None
)

agent = create_react_agent(
    model,
    [*resume_tailoring_tools, *user_experience_gathering_tools, get_user_files_paths],
)

MAX_HISTORY = 20  # or whatever fits your model's context window
