from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
from .tailor_resume.tools import tailor_resume_tools
from .update_user_profile.tools import update_user_profile_tools
from .write_cover_letter.tools import write_cover_letter_tools
from .assess_resume_as_company.tools import access_resume_as_company_tools
from tools.supabase_storage_tools import get_user_files_paths

# Initialize the model
model = ChatAnthropic(
    model_name="claude-3-7-sonnet-latest",
    timeout=120,
    stop=None
)

agent = create_react_agent(
    model,
    [
        *tailor_resume_tools,
        *update_user_profile_tools,
        *write_cover_letter_tools,
        *access_resume_as_company_tools,
        get_user_files_paths,
    ],
)
