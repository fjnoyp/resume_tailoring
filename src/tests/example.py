# NOT TESTED: the files for the current user and job are not available in Supabase yet
# TODO: implement AI Unit Tests for each module based on this (create particular evaluators and calls for each)

from dotenv import load_dotenv

load_dotenv()

import asyncio
from langsmith import Client
from langsmith.evaluation import StringDistanceEvaluator
from full_tailor_resume.resume_tailoring_agent import agent
from src.tools.state_storage_manager import StateStorageManager
from src.tools.file_path_manager import get_file_paths
from openevals.llm import create_llm_as_judge
from openevals.prompts import (
    CORRECTNESS_PROMPT,
    RELEVANCE_PROMPT,
    CONCISENESS_PROMPT,
    FLUENCY_PROMPT,
)
import logging

logging.basicConfig(level=logging.INFO)

client = Client()

# === Test cases for 'against ideal' evaluation ===
# For each test case, we must provide:
#  - the supabase input files (full resume, job description, original resume) for the user and job
#  - in the "job_id/ideal_outputs/" directory, the ideal output files (tailored resume, cover letter) for the user and job
#  - the user_id and job_id for the test case in this list
TEST_CASE_IDS = [
    {"user_id": "test_user_001", "job_id": "test_job_001"},
]


async def fetch_test_case_inputs(user_id, job_id):
    """
    Fetch the test case input files from Supabase Storage for a given user_id and job_id.
    """
    file_paths = get_file_paths(user_id, job_id)
    job_description = (
        await StateStorageManager._load_file_content(file_paths.job_description_path)
        or ""
    )
    reference_resume = (
        await StateStorageManager._load_file_content(file_paths.original_resume_path)
        or ""
    )
    full_resume = (
        await StateStorageManager._load_file_content(file_paths.user_full_resume_path)
        or ""
    )

    if not job_description or not reference_resume or not full_resume:
        logging.warning(f"Missing input files for {user_id}/{job_id}")

    return {
        "user_id": user_id,
        "job_id": job_id,
        "job_description": job_description,
        "reference_resume": reference_resume,
        "full_resume": full_resume,
    }


async def fetch_ideal_outputs(user_id, job_id):
    """
    Fetch the ideal output files (tailored resume and cover letter) from Supabase Storage for a given user_id and job_id.
    """
    tailored_resume = (
        await StateStorageManager._load_file_content(
            f"{user_id}/{job_id}/ideal_outputs/TAILORED_RESUME.md"
        )
        or ""
    )
    cover_letter = (
        await StateStorageManager._load_file_content(
            f"{user_id}/{job_id}/ideal_outputs/COVER_LETTER.md"
        )
        or ""
    )

    if not tailored_resume or not cover_letter:
        logging.warning(f"Missing ideal output files for {user_id}/{job_id}")

    return {
        "tailored_resume": tailored_resume,
        "cover_letter": cover_letter,
    }


async def target(inputs: dict) -> dict:
    """
    Call the agent to generate outputs and then fetch the results from Supabase Storage.
    """
    user_id = inputs["user_id"]
    job_id = inputs["job_id"]

    # 1. Call the agent (this writes results to Supabase)
    prompt = (
        f"enhance my resume against my current job id, and then write a cover letter. "
        f"{{user_id: {user_id}, job_id: {job_id}}}"
    )
    logging.info(f"Calling agent for {user_id}/{job_id}")
    await agent.ainvoke({"input": prompt})

    # 2. Read the results using StateStorageManager
    file_paths = get_file_paths(user_id, job_id)
    tailored_resume = (
        await StateStorageManager._load_file_content(file_paths.tailored_resume_path)
        or ""
    )
    cover_letter = (
        await StateStorageManager._load_file_content(file_paths.cover_letter_path) or ""
    )

    if not tailored_resume or not cover_letter:
        logging.warning(f"Missing agent output files for {user_id}/{job_id}")

    return {"tailored_resume": tailored_resume, "cover_letter": cover_letter}


def example_exists(existing_examples, inputs):
    """
    Check if an example with the same user_id and job_id already exists in the dataset.
    """
    for ex in existing_examples:
        ex_inputs = ex.inputs
        if (
            ex_inputs.get("user_id") == inputs["user_id"]
            and ex_inputs.get("job_id") == inputs["job_id"]
        ):
            return True
    return False


async def main():
    """
    Main entry point: create dataset, add missing examples, and run evaluation.
    """
    ideal_dataset_name = "Resume Tailoring - Against Ideal"
    try:
        ideal_dataset = client.create_dataset(
            dataset_name=ideal_dataset_name,
            description="Dataset for evaluating outputs against ideal references.",
        )
        logging.info(f"Created new dataset: {ideal_dataset_name}")
    except Exception:
        datasets = list(client.list_datasets(dataset_name=ideal_dataset_name))
        ideal_dataset = datasets[0]
        logging.info(f"Using existing dataset: {ideal_dataset_name}")

    # Add missing examples only
    existing_examples = list(client.list_examples(dataset_id=ideal_dataset.id))
    for test_case in TEST_CASE_IDS:
        inputs = await fetch_test_case_inputs(test_case["user_id"], test_case["job_id"])
        ideal_output = await fetch_ideal_outputs(
            test_case["user_id"], test_case["job_id"]
        )
        if not example_exists(existing_examples, inputs):
            client.create_example(
                dataset_id=ideal_dataset.id, inputs=inputs, outputs=ideal_output
            )
            logging.info(
                f"Added example for {test_case['user_id']}/{test_case['job_id']}"
            )
        else:
            logging.info(
                f"Example already exists for {test_case['user_id']}/{test_case['job_id']}"
            )

    # Examples: openevals LLM-as-a-judge evaluators for correctness, relevance, conciseness, and fluency
    correctness_evaluator = create_llm_as_judge(
        prompt=CORRECTNESS_PROMPT,
        feedback_key="correctness",
        model="openai:o3-mini",
    )
    relevance_evaluator = create_llm_as_judge(
        prompt=RELEVANCE_PROMPT,
        feedback_key="relevance",
        model="openai:o3-mini",
    )
    conciseness_evaluator = create_llm_as_judge(
        prompt=CONCISENESS_PROMPT,
        feedback_key="conciseness",
        model="openai:o3-mini",
    )
    fluency_evaluator = create_llm_as_judge(
        prompt=FLUENCY_PROMPT,
        feedback_key="fluency",
        model="openai:o3-mini",
    )

    evaluators = [
        correctness_evaluator,
        relevance_evaluator,
        conciseness_evaluator,
        fluency_evaluator,
    ]

    logging.info(f"Running evaluation with {evaluators}...")
    await client.aevaluate(
        target,
        data=ideal_dataset_name,
        evaluators=evaluators,
        experiment_prefix="resume-tailoring-ideal",
        max_concurrency=2,
    )
    logging.info("Evaluation complete.")


if __name__ == "__main__":
    asyncio.run(main())
