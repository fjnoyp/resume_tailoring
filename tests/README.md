## Overview

This folder contains the **AI unit tests** for the Resume Tailoring system. The goal is to ensure the quality, reliability, and continuous improvement of all AI modules by evaluating their outputs against ideal references and well-defined criteria.

## Approach *(Planned)*

- **Input/Output Datasets:**
  - Each test case specifies user/job input files (e.g., resumes, job descriptions) and corresponding ideal outputs (e.g., tailored resumes, cover letters).
  - Ideal outputs are used as ground truth for evaluation.

- **Automated Evaluation:**
  - Tests are implemented as scripts (see [example.py](example.py)) that:
    - Fetch test case data from storage (e.g., Supabase).
    - Call the relevant AI module to generate outputs.
    - Compare generated outputs to ideal outputs using automated evaluators.
  - Automated evaluators are designed to:
    - Perform ATS analysis and identify missing ATS keywords, providing an ATS match score.
    - Score each line or sentence in the job description and resume for relevance and alignment.
    - Map job description requirements to resume content, highlighting matches and gaps.
    - Identify key requirements and provide granular details that would lead to an accept or reject decision.
    - Support incremental scoring to track improvements over time.

- **Module-Level Testing:**
  - Each AI module (e.g., resume tailoring, cover letter generation) will have dedicated tests and evaluators.
  <!--
  - The structure and approach will be based on the implementation in [example.py](example.py).
  -->

## Implementation Notes

- Tests are designed to be extensible: add new test cases, evaluators, or modules as the system evolves.
- The evaluation framework supports both adding new examples and running batch evaluations.