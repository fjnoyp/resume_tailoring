## Overview

This folder contains the **Backend AI System** for the Resume Tailoring platform. It provides the core AI-driven workflow for tailoring resumes, managing user profiles, and generating application materials. The system is designed to be modular, with each submodule handling a specific aspect of the resume tailoring process.

## Main Orchestration

The main orchestration is handled by [`main_agent.py`](./main_agent.py), which:
- Loads and configures the AI model and tools.
- Calls each submodule as a tool, coordinating the overall resume tailoring workflow.
- Ensures extensibility and modularity, allowing each submodule to be improved independently.

## Submodules

Each submodule is implemented as a directory containing the logic for a specific part of the workflow:

- **assess_resume_as_company/**
  - Simulates a company's perspective to assess the user's resume.
  - (Planned) May impersonate the company by researching its profile and hiring needs.
  - Generates recruiter-style analysis and feedback.

- **tailor_resume/**
  - Produces a tailored resume based on company feedback and the user's full profile.
  - Prompts the user for missing or critical information, with suggestions and importance ratings.
  - Generates a tailored resume and a detailed explanation of tailoring decisions.

- **tailor_cv/** *(Planned)*
  - (Planned) Produces a tailored CV for roles or regions where a CV is required.

- **update_user_profile/**
  - Updates and maintains the user's master profile/resume as new information is provided.

- **write_cover_letter/**
  - Generates a tailored cover letter for the job application, leveraging the tailored resume and company feedback.

## Design Principles

- **Modularity:** Each submodule can be developed, tested, and improved independently.
- **Transparency:** The system provides clear explanations for all tailoring decisions.
- **User-Centric:** Prompts users only for information that is missing or critical, with guidance on importance.

## Future Directions

- Integrate with a separate output grading module for ATS and recruiter analysis (see [output_grading](../output_grading/README.md)).
- Integrate with a separate AI unit testing suite (see [tests](../tests/)).
- Expand company impersonation and feedback generation.