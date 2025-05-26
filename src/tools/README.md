## Overview

This folder contains helper tools that support the core functionality of the Resume Tailoring platform. These tools provide essential services such as file parsing, storage management, and integration with external systems. They are designed to be modular and reusable across different parts of the codebase, including the backend AI system, evaluation scripts, and other modules.

## Storage Architecture Overview

This folder contains the storage management system for the Resume Tailoring platform. The architecture is designed with clear separation of concerns and controlled access patterns.

### Architecture Components

#### 1. **StateStorageManager** (`state_storage_manager.py`) - **PRIMARY INTERFACE**
- **Main public interface** for all storage operations
- Provides high-level, state-aware operations
- Handles loading/saving of state fields with proper validation
- **All nodes should use this interface**

#### 2. **File Path Manager** (`file_path_manager.py`) - **PATH UTILITIES**
- Centralized path management for all user and job files
- Type-safe path generation with `UserFilePaths` class
- Prevents magic strings and path construction errors

#### 3. **Private Storage Implementation** (`_supabase_storage_tools.py`) - **INTERNAL ONLY**
- Low-level Supabase storage operations
- **Private module** (underscore prefix) - should NOT be imported directly
- Only used internally by StateStorageManager

#### 4. **Storage Tools** (`storage_tools.py`) - **AGENT TOOLS**
- LangChain-compatible tools for agents that need storage access
- Uses StateStorageManager as backend
- For use in agent workflows that require file operations

### Usage Patterns

#### ✅ **CORRECT - Use StateStorageManager**
```python
from src.tools.state_storage_manager import StateStorageManager, load_resume_tailoring_data

# Load state data
result = await load_resume_tailoring_data(user_id, job_id)
if result.success:
    job_description = result.loaded_fields["job_description"]

# Save processing results
await StateStorageManager.save_state_field(user_id, job_id, "tailored_resume", content)

# Read custom files
file_content = await StateStorageManager.read_file(user_id, "resume.pdf")
```

#### ✅ **CORRECT - Use File Path Manager for paths**
```python
from src.tools.file_path_manager import get_file_paths

file_paths = get_file_paths(user_id, job_id)
resume_path = file_paths.tailored_resume_path
```

#### ✅ **CORRECT - Use Storage Tools for agents**
```python
from src.tools.storage_tools import storage_tools
from langgraph.prebuilt import create_react_agent

agent = create_react_agent(model, storage_tools)
```

#### ❌ **INCORRECT - Direct storage access**
```python
# DON'T DO THIS
from src.tools._supabase_storage_tools import _read_file_from_bucket
```

### Key Benefits

1. **Single Source of Truth**: StateStorageManager is the only public interface
2. **Type Safety**: File paths are managed centrally with type checking
3. **Maintainability**: Changes to storage implementation only affect private modules
4. **Consistency**: All nodes use the same interface patterns
5. **Error Handling**: Centralized error handling and logging

### Migration Guide

If you have existing code using the old `supabase_storage_tools`:

**Old:**
```python
from src.tools.supabase_storage_tools import read_file_from_bucket, get_file_paths

file_paths = get_file_paths(user_id, job_id)
content_bytes = await read_file_from_bucket(file_paths.resume_path)
content = content_bytes.decode("utf-8") if content_bytes else ""
```

**New:**
```python
from src.tools.state_storage_manager import StateStorageManager
from src.tools.file_path_manager import get_file_paths

file_paths = get_file_paths(user_id, job_id)
content = await StateStorageManager._load_file_content(file_paths.resume_path) or ""
```

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