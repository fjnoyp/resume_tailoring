
# Functionality 

- Need structured output 
- Seems wrong to have read file tools - we should pass all relevant info directly and reference it in the prompt template as a $var. 


# Data Needed

### User provided: 
- Current Resume 
- Full User Picture
- Job description 

### Artifacts: 
- Resume screener notes 
- Extra company info? 




We need to think in terms of artifacts 
Each AI step/module gives an output (please note I use step/module interchangeably)

AI steps communciate via artifacts 

We should only share a chat history where necessary - chat history adds noise and makes it harder to debug ai steps 

Each step must run independently to allow proper AI scaling + unit testing 

We should only rely on AI calling of arbitrary tools / agentic ai when necessary. Otherwise the overall resume tailoring process should be treated as a hardcoded chain of preset steps that go to other steps (module). 

The only place for tool calling should be the resume rewriter. The user feedback tool should prompt the user for information, but the user might give back incomplete information or more information might be necessary, necessiting resume rewriter step to choose to call that tool again, etc. 

Overall not relying on the AI to call tools, and making the transitions between the ai steps hardcoded via a chain will make it easier to debug the system, and write unit tests for each step (module) and make it much easier to reason about what the system is doing and where it might be failing. 


Below, we should identify all the ai modules/steps, what each should do, and what their inputs/outputs are. 

# Job Description Analyzer 
Convert Job Description -> Company Requirements 
- Input: Job Description 
- Output: Job Strategy (document) 

- Understand the psychology of the company and the recruiters 

# Recruiter Step 
Given Company Requirements assess give feedback on a resume. 
- Input: Job Description / Job Strategy / CurrentResume
- Output: Recruiter Feedback (document) 

- Given the job specs, write a feedback report on the resume 

# Resume Rewriter
Given feedback, rewrite the resume 
- Input: Job Description / Job Strategy / Recruiter Feedback / CurrentResume 
- Output: UpdatedCurrentResume

- Should have the getUserInfo tool to get missing information 
- Rewrite the resume to cover any weaknesses

Let's focus on getting the above steps right first. Then we can focus on having a feedback step between Resume Recruiter -> Recruiter Step as well as having an ATS checker step in the Recruiter Step to get an ATS score. 

(Let me know when you finish the above step - the next steps are as follows but we sholud discuss first: )

Afterwards we should start focusing on generating a score. We would have an LLM as Judge give a 0/1 output on a AI generated list of requirements + General Resume requirements like: 
1. (Ai Generated) Matches roles need for expert in Java with GraalVM etc. 
2. (Generated) Experience A quantifies impact / Experience B quantifies impact etc. 

This way we can construct a total score based on the weighted aggregation of all these outputs. 



# Cover Letter Rewriter 
TODO 