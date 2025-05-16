
## Current Goal 

Make a resume tailoring system that our test users love. 

Our assumption - users want a tailored resume, but beyond ATS matching or trying to match the job description, don't know exactly how to tailor a resume for a company at a strategic level and don't actually want to spend time tweaking each resume ... They just need a solution they can trust ... 

Other system do resume tailoring, we need a one click solution that creates an improved resume, seamlessly asks user for any missing information, and sufficiently explains to the user why the new resume is better for the job description.

## Approach Requirements: 

- Basic website flow 
    - User account creation/login     
    - User profile management 
        - User uploads initial resume + linkedin         
        - AI maintains a 'master' full resume 
        - Full resume forms basis for tailoring for all future jobs. 
        - (Later) AI does a basic generic rewrite of the resume to improve a generic resume score (TBD)         
        - (Later) allow users to data dump any extra information - design documents, github links, slack message history etc. - and have ai intelligently update the user's profile 
        - (Later) Any future information provided by user appends to this full resume         
    - Job Sections 
        - User has a list of jobs with ability to create a new job section 
        - Each job section contains: 
            - Job description that user pastes in (for now) to create that job section 
            - Tailored resume 
            - Tailored CV 
            - Comments - company feedback, reasons why tailored content is better or missing etc. 

- AI System  
    - Backend AI System 
        - Note: Each aspect of the AI system should be a self contained module - this will allow us to call them independently to iterate on the quality of each module output 
        - full-tailor-resume - full flow for tailoring a resume that calls all the sub modules 
            - assess-resume-as-company
                - (Later) Impersonate company 
                    - Perform web search on company
                    - Create a profile of the company 
                    - Identify general hiring needs based on job description + company profile                     
                - Assess whether resume fits company
                    - Perform a recruiter/reviewer analysis
                    - Generate the CompanyFeedback file 
                    
            - tailor-resume
                - Take CompanyFeedback file 
                - Take Full User Profile (originally resume full) 
                - Calls a 'ask-user' tool that prompts the user for missing information 
                    - This step should auto generate several suggestions based on the user's profile on what the answer's might be, and what an ideal answer could be, AND how important the missing information is (ie. not answering this would cause a critical requirement to be missing etc.) 
                - Tailor resume + provide full analysis/description on why it was tailored in this way 

            - tailor-cv 
    - Output Grading 
        - (Later) Build upon the assess-resume-as-company module to generate detailed metrics/ratings on how well the resume scores, we need to identify the metrics to generate a score 
            - Perform ATS analysis and identify missing ATS keywords + give a ATS match score 
            - Give a score for each line / sentence in the job description and how well the resume matches that, and which lines in the resume match to each line in the job description and by how much 
            - Give a score for each line / sentence in the resume and how well it matches the job description, and which lines in the job description match to each line in the resume and by how much 
            - Identify key requirements from job description, and score how well resume matches 
            - Overall, identify the granular details of the job description + resume that would lead to a accept/reject and make those details obvious to the user 
            - We need an incremental score that we can increase over time with clarity on how it's increasing 
    - AI Unit Tests (Langsmith) 
        - We need a basic input dataset + ideal output dataset and a series of AI evaluators 
        - We should be able to run tests on demand at a module level to assess how well the current/latest ai output matches the expectations we specified in our ideal output dataset 
            - This is TBD as we don't know the ideal output for each module yet ... we may need to reach out to recruiters to understand what the ideal output of each step should be 


                