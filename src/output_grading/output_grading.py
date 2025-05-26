from dotenv import load_dotenv

# Load environment variables
load_dotenv()

import asyncio
from langsmith import Client
from src.output_grading.cover_letter_evaluator import cover_letter_evaluator
from src.output_grading.resume_tailoring_evaluator import resume_tailoring_evaluator
from src.tools.supabase_storage_tools import get_file_paths, read_file_from_bucket
import argparse

client = Client()
dataset_name = "Resume Tailoring Evaluator"


async def target(inputs: dict) -> dict:
    user_id = inputs["user_id"]
    job_id = inputs["job_id"]

    # Get canonical file paths for this user/job
    file_paths = get_file_paths(user_id, job_id)

    # Read files from Supabase
    tailored_resume_bytes = await read_file_from_bucket(file_paths.tailored_resume_path)
    cover_letter_bytes = await read_file_from_bucket(file_paths.cover_letter_path)

    tailored_resume = (
        tailored_resume_bytes.decode("utf-8") if tailored_resume_bytes else ""
    )
    cover_letter = cover_letter_bytes.decode("utf-8") if cover_letter_bytes else ""

    return {"tailored_resume": tailored_resume, "cover_letter": cover_letter}


async def fetch_inputs_for_example(user_id, job_id):
    file_paths = get_file_paths(user_id, job_id)
    job_description_bytes = await read_file_from_bucket(file_paths.job_description_path)
    reference_resume_bytes = await read_file_from_bucket(
        file_paths.original_resume_path
    )
    full_resume_bytes = await read_file_from_bucket(file_paths.user_full_resume_path)

    return {
        "user_id": user_id,
        "job_id": job_id,
        "job_description": (
            job_description_bytes.decode("utf-8") if job_description_bytes else ""
        ),
        "reference_resume": (
            reference_resume_bytes.decode("utf-8") if reference_resume_bytes else ""
        ),
        "full_resume": full_resume_bytes.decode("utf-8") if full_resume_bytes else "",
    }


async def run_evaluation(user_id, job_id):
    example_inputs = await fetch_inputs_for_example(user_id, job_id)

    try:
        dataset = client.create_dataset(
            dataset_name=dataset_name,
            description="A dataset for the resume tailoring agent.",
        )
        examples = [{"inputs": example_inputs}]
        client.create_examples(dataset_id=dataset.id, examples=examples)
    except:
        datasets = list(client.list_datasets(dataset_name=dataset_name))
        dataset = datasets[0]

    # Evaluate the AI response
    await client.aevaluate(
        target,
        data=dataset_name,
        evaluators=[resume_tailoring_evaluator, cover_letter_evaluator],
        experiment_prefix="resume-tailoring",
        max_concurrency=2,
    )


async def main():
    parser = argparse.ArgumentParser(description="Run the resume tailoring evaluator.")
    parser.add_argument("--user-id", required=True, help="The user ID")
    parser.add_argument("--job-id", required=True, help="The job ID")
    args = parser.parse_args()

    user_id = args.user_id
    job_id = args.job_id

    await run_evaluation(user_id, job_id)


if __name__ == "__main__":
    asyncio.run(main())
