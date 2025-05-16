# Plan

### The Challenge: AI in Job Hunting

AI is increasingly used in hiring for application screening, analysis, and even task execution. This presents challenges and opportunities:
*   **Increased Competition:** AI tools enable mass applications, raising the bar for quality.
*   **Stricter Screening:** Companies use AI to filter candidates overwhelmed by volume.
*   **Evolving Job Market:** AI may reduce the number of available roles.
*   **Necessity of AI:** Using AI in job searching is becoming crucial for a competitive edge. Manual applications are too slow.

Why Tech Companies Are Pulling Job Listings
https://www.youtube.com/watch?v=7t_HC8WleDY&ab_channel=EconomyMedia



### Current Tool Limitations

Existing AI resume tools are inadequate for effective tailoring, often focusing on superficial aspects:

*   **Superficial Analysis:** Many prioritize scores (e.g., Huntr's "match score"), basic ATS keyword optimization (e.g., ResumeTailor.ai, RankResume.io), or simple intro/bullet point generation.
*   **Lack of Depth:** They primarily match existing resume text to job descriptions, failing to capture a candidate's full experience or prompt for relevant missing details required by the role.
*   **Missing Recruiter Perspective:** Tools focus on keyword presence rather than analyzing the underlying skills, experience patterns, or cultural fit recruiters seek.
*   **Weak Cover Letter Integration:** When offered (e.g., Huntr, RankResume.io), cover letters often seem like a separate, templated feature rather than a strategic tool to address specific resume gaps.
*   **Pricing Models:** Often involve limited free tiers followed by subscriptions (e.g., Huntr: $40/mo, ResumeTailor.ai: ~$8/mo) or credit systems (e.g., RankResume.io: pay-per-resume after free credits).

*(Initial validation based on web search - see links below)*

TODO: create a detailed matrix of competitors (e.g., ResumeTailor.ai [https://resumetailor.ai/], Huntr [https://huntr.co/product/resume-tailor], RankResume.io [https://www.rankresume.io/], Rezi.ai [https://www.rezi.ai/], Teal [https://www.tealhq.com/], Kickresume [https://www.kickresume.com/en/], Jobscan [https://www.jobscan.co/], Enhancv [https://enhancv.com/], Zety, Resume Genius) and their specific pros/cons.

(TODO) - we need to validate the above assertions and have an adversarial bot to probe for weaknesses in any assumptions

### Proposed Solution: Deep AI Resume Tailoring

We propose an AI-assisted tool addressing these limitations through a multi-agent system:

1.  **Comprehensive User History Gathering:**
    *   Collects full experience via interactive methods (voice/text), as well as from LinkedIn or existing resumes.
    *   Proactively prompts for relevant experiences based on target roles, addressing common user forgetfulness.
    *   (TBD - explore proactive/reactive prompting)

2.  **Job & Company Requirements Analysis Agent:**
    *   Analyzes job postings and other company information (e.g., website, news) to extract key required skills, experiences, implied cultural elements, and potential evaluation criteria.
    *   Establishes a consistent grading/evaluation framework for iterative resume/cover letter improvement.

3.  **Resume Rewrite Expert Agent:**
    *   Tailors the resume based on insights from the Requirements Analysis Agent.
    *   Identifies experience *and skill* gaps and prompts the user via the History Gatherer.
    *   Iterates with the Requirements Analysis Agent (Step 3 -> 2 loop) to refine the resume.

4.  **Skill Gap Analysis & Guidance:**
    *   Explicitly identifies key skills from the job description that appear missing or underrepresented in the user's gathered history.
    *   Potentially suggests areas for upskilling or how to frame existing experience to better match requirements.

5.  **Strategic Cover Letter Writer:**
    *   Complements the tailored resume by addressing remaining weaknesses or skill/experience gaps identified during the rewrite and analysis process.

6.  **Targeted Interview Preparation:**
    *   Leverages the job/company analysis to generate tailored practice interview questions, potential talking points, and relevant company research summaries.

7.  **User Education & Reasoning:**
    *   Provides summarized reasoning behind tailoring decisions, guiding users on company expectations and how to present their skills/attitude effectively in resumes and interviews.