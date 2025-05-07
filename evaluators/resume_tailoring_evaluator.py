from openevals import create_llm_as_judge

def resume_tailoring_evaluator_prompt(inputs, outputs, reference_outputs, **kwargs):
    return f"""
You are an expert recruiter and resume reviewer evaluating how well a tailored resume matches a specific job description. Your task is to assign a score based on the following rubric:

<Rubric>
A highly effective tailored resume:
- Demonstrates clear alignment with the job description through relevant experiences and skills (SHOW, DO NOT TELL)
- Highlights quantifiable achievements and results, using subtle, evidence-backed claims
- Appropriately incorporates and adapts information from @resume.md and, if relevant, @linked-in.md, @seren-ai-flutter-readme.md, and @seren-ai-langgraph-readme.md
- Maintains clarity, professionalism, and error-free language
- Uses job description keywords naturally for ATS optimization
- Presents a clear, readable, and well-structured format
- Emphasizes unique skills, personal branding, and career goals
- Ends with a professional, enthusiastic call to action
- Reflects understanding of company culture and values
- Avoids exaggeration, unsupported claims, or irrelevant information
- Retains and appropriately adapts the open source AI agentic side project experience, as it is a key differentiator

When scoring, you should penalize:
- Generic or boilerplate content that does not address the job description
- Factual inaccuracies, unsupported claims, or exaggerations
- Omission of key, relevant experiences or quantifiable results
- Unprofessional language, jargon, or formatting issues
- Failure to use or misuse of job description keywords
- Lack of clear structure or readability
- Overly verbose or redundant information
- Ignoring strategic company/culture fit or recruiter perspective

</Rubric>

<Instructions>
- Carefully read the job description and the tailored resume
- Compare the tailored resume against the job description and the guidance in @general_resume_advice_prompt.py
- Check for evidence of customization, clarity, achievements, and strategic alignment
- Identify both strengths and weaknesses, citing specific examples
- Focus on practical impact and recruiter appeal, not just surface-level matching
- Consider both explicit and implicit requirements of the job description
</Instructions>

<Reminder>
- The goal is to evaluate how well the resume is tailored to the job description and how effectively it positions the candidate for the specific role.
- Focus on strategic alignment, evidence-backed claims, and recruiter perspective.
- Ignore style preferences unless they impact professionalism or clarity.
</Reminder>

<job_description>
{inputs["job_description"]}
</job_description>

<tailored_resume>
{outputs["tailored_resume"]}
</tailored_resume>

<reference_resume>
{inputs["reference_resume"]}
</reference_resume>
"""

resume_tailoring_evaluator = create_llm_as_judge(
    prompt=resume_tailoring_evaluator_prompt,
    model="anthropic:claude-3-5-sonnet-latest",
    feedback_key="output_quality",
)