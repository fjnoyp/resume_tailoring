## Overview

This folder contains helper tools that support the core functionality of the Resume Tailoring platform. These tools provide essential services such as file parsing, storage management, and integration with external systems. They are designed to be modular and reusable across different parts of the codebase, including the backend AI system, evaluation scripts, and other modules.

## Tools Provided

- **supabase_storage_tools.py**
  - Provides async functions for interacting with Supabase Storage.
  - Used to upload, download, list, and delete user/job-related files (resumes, job descriptions, tailored outputs, etc.).
  - Supplies canonical file path utilities for consistent file management across the platform.

- **parse_pdf_tool.py**
  - Extracts text from PDF files using `pdfplumber`.
  - Used to convert uploaded PDF resumes or documents into plain text for further processing by AI modules.

- **mcp_agent.py**
  - Contains integration utilities for interacting with MCP (Model Context Protocol) servers, enabling standardized, context-aware communication between AI agents and external services (e.g., currently used for connecting to a LinkedIn MCP server).
  - Used for advanced server-side operations or external service calls as needed by the platform.

## Usage

- These tools are imported and used by the main backend AI modules, evaluation scripts, and other utility scripts.
- They are designed to be called as standalone functions or grouped as toolkits for agent-based workflows.

## Design Principles

- **Reusability:** Each tool is written to be easily reused across different modules and scripts.
- **Modularity:** Tools are self-contained and can be extended or replaced as needed.
- **Asynchronous Support:** Tools are async to support scalable, non-blocking workflows.

## Extending

To add a new tool, create a new Python file in this folder and ensure it follows the modular, documented style of the existing tools. Update relevant imports in other modules as needed. 