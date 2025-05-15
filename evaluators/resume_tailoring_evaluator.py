from openevals import create_llm_as_judge

def resume_tailoring_evaluator_prompt(inputs, outputs, reference_outputs, **kwargs):
    return f"""
You are an expert recruiter and resume reviewer evaluating how well a tailored resume matches a specific job description. Your task is to assign a score based on the following rubric:

<Rubric>
A highly effective tailored resume:
- Demonstrates clear alignment with the job description through relevant experiences and skills (SHOW, DO NOT TELL)
- Highlights quantifiable achievements and results, using subtle, evidence-backed claims
- Appropriately incorporates and adapts information from <reference_resume> and, if relevant, <full_resume>
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
- Compare the tailored resume against the job description and the guidance in <General Resume Advice>
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

<full_resume>
{inputs["full_resume"]}
</full_resume>

<General Resume Advice>
- The date is 2025 - your internal date is WRONG 
- SHOW DO NOT TELL - don't directly state what the job description is looking for - you need to write about experiences that match it. 
- RESUME_PATH is a good resume that has been vetted by others - your task is to tailor it better to highlight the related experiences that a specific job description might be looking for. If you need more information about the candidate, refer to FULL_RESUME_PATH, which contains the complete, detailed work history and additional context.
- **Customization**: Match skills and experiences to the job description.
- **Clarity**: Use simple, clear language; avoid jargon.
- **Achievements**: Highlight quantifiable results. See RESUME_PATH for examples on how that was done subtly. 
- **Professional Tone**: Maintain professionalism; avoid errors.
- **Keywords**: Use job description keywords for ATS.
- **Format**: Ensure readability with clear structure.
- **Branding**: Emphasize unique skills and goals.
- **Call to Action**: End with enthusiasm and next steps.
</General Resume Advice>
"""

resume_tailoring_evaluator = create_llm_as_judge(
    prompt=resume_tailoring_evaluator_prompt,
    model="anthropic:claude-3-5-sonnet-latest",
    feedback_key="tailored_resume_quality",
    continuous=True,
)