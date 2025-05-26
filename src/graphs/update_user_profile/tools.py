from ..info_collection.update_user_full_resume import update_user_full_resume
from .parse_linkedin_profile import parse_linkedin_profile
from .convert_text_to_resume_markdown import parse_additional_file

update_user_profile_tools = [
    update_user_full_resume,
    parse_linkedin_profile,
    parse_additional_file,
]
