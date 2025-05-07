
from openevals import create_llm_as_judge

def cover_letter_evaluator_prompt(inputs, outputs, reference_outputs, **kwargs):
    return f"""
You are an expert recruiter and cover letter reviewer evaluating how well a cover letter supports a candidate's application for a specific job. Your task is to assign a score based on the following rubric:

<Rubric>
A highly effective cover letter:
- Demonstrates clear alignment with the job description and company values through relevant experiences and skills (SHOW, DO NOT TELL)
- Provides a compelling narrative that complements the resume, addressing both strengths and potential weaknesses or gaps
- Highlights quantifiable achievements and unique value, using subtle, evidence-backed claims
- Appropriately incorporates and adapts information from @resume.md, @linked-in.md, and, if relevant, @seren-ai-flutter-readme.md and @seren-ai-langgraph-readme.md
- Maintains clarity, professionalism, and error-free language
- Uses job description keywords naturally for ATS optimization
- Is concise (200-500 words), focused, and avoids redundancy or generic statements
- Presents a clear, readable, and well-structured format
- Demonstrates understanding of the company, role, and recruiter perspective
- Addresses or mitigates any weaknesses or concerns raised in recruiter feedback (if provided), ideally in an indirect, positive manner
- Ends with a professional, enthusiastic call to action
- Is unique, memorable, and tailored to the specific opportunity

When scoring, you should penalize:
- Generic, boilerplate, or verbose content that does not address the job description or company
- Factual inaccuracies, unsupported claims, or exaggerations
- Omission of key, relevant experiences or failure to address known weaknesses
- Unprofessional language, jargon, or formatting issues
- Failure to use or misuse of job description keywords
- Lack of clear structure or readability
- Overly verbose, redundant, or unfocused information
- Ignoring strategic company/culture fit or recruiter perspective
- Failing to complement or add value beyond the resume

</Rubric>

<Instructions>
- Carefully read the job description, the cover letter, and the candidate's resume
- Compare the cover letter against the job description, recruiter feedback (if any), and best practices for cover letters
- Check for evidence of customization, clarity, achievements, and strategic alignment
- Identify both strengths and weaknesses, citing specific examples
- Focus on practical impact, recruiter appeal, and how the cover letter enhances the overall application
- Consider both explicit and implicit requirements of the job description and company
</Instructions>

<Reminder>
- The goal is to evaluate how well the cover letter is tailored to the job description and how effectively it positions the candidate for the specific role
- Focus on strategic alignment, evidence-backed claims, and recruiter perspective
- Ignore style preferences unless they impact professionalism or clarity
- Consider the cover letter's ability to address or mitigate weaknesses and to add value beyond the resume
</Reminder>

<job_description>
{inputs["job_description"]}
</job_description>

<cover_letter>
{outputs["cover_letter"]}
</cover_letter>

<tailored_resume>
{outputs["tailored_resume"]}
</tailored_resume>
"""

cover_letter_evaluator = create_llm_as_judge(
        prompt=cover_letter_evaluator_prompt,
        model="anthropic:claude-3-5-sonnet-latest",
        feedback_key="output_quality",
        continuous=True,
    )