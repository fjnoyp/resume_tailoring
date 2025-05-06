import asyncio
from langsmith import Client
from openevals.llm import create_llm_as_judge
from prompts.resume_tailoring_evaluation_prompt import RESUME_TAILORING_EVALUATION_PROMPT
from prompts.cover_letter_evaluation_prompt import COVER_LETTER_EVALUATION_PROMPT
from resume_tailoring_agent import process_query
from samples.inputs import FULL_RESUME, JOB_DESCRIPTION, REFERENCE_RESUME

client = Client()

resume_tailoring_evaluator = create_llm_as_judge(
        prompt=RESUME_TAILORING_EVALUATION_PROMPT,
        model="anthropic:claude-3-5-sonnet-latest",
        feedback_key="output_quality",
    )

cover_letter_evaluator = create_llm_as_judge(
        prompt=COVER_LETTER_EVALUATION_PROMPT,
        model="anthropic:claude-3-5-sonnet-latest",
        feedback_key="output_quality",
    )

async def target(inputs: dict) -> dict:
#     await process_query(f"""Can you help me enhance my resume and write a cover letter for this job?

# <Job Description>
# {inputs["job_description"]}
# </Job Description>

# <Resume>
# {inputs["reference_resume"]}
# </Resume>

# <Full Resume>
# {inputs["full_resume"]}
# </Full Resume>
# """)
    with open("samples/resume.md", "r", encoding="utf-8") as f:
        tailored_resume = f.read()
    with open("cover-letter.md", "r", encoding="utf-8") as f:
        cover_letter = f.read()
    return {
        "tailored_resume": tailored_resume,
        "cover_letter": cover_letter
    }

async def main():
    # Initialize (or get) the dataset
    try:
        dataset = client.create_dataset(
            dataset_name="Resume Tailoring", description="A dataset for the resume tailoring agent."
        )
        examples = [
            {
                "inputs": {
                    "job_description": JOB_DESCRIPTION,
                    "reference_resume": REFERENCE_RESUME,
                    "full_resume": FULL_RESUME
                }
            }
        ]
        client.create_examples(dataset_id=dataset.id, examples=examples)
    except:
        datasets = list(client.list_datasets(dataset_name="Resume Tailoring"))
        dataset = datasets[0]

    for example in client.list_examples(dataset_id=dataset.id):
        print("Example inputs:", example.inputs)

    # Evaluate the AI response
    await client.aevaluate(
        target,
        data="Resume Tailoring",
        evaluators=[
            resume_tailoring_evaluator,
            cover_letter_evaluator
        ],
        experiment_prefix="resume-tailoring",
        max_concurrency=2,
    )

if __name__ == "__main__":
    asyncio.run(main())