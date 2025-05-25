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

# Resume Tailoring AI Graph

A LangGraph-based AI system for automatically tailoring resumes to specific job descriptions with clean, maintainable architecture.

## Architecture Overview

This system uses a **simplified flat state structure** with clear field ownership and **centralized file I/O** for maximum maintainability.

### Simplified State Structure

```python
GraphState = {
    # Context (immutable)
    "user_id": str,
    "job_id": str,
    
    # Input data (loaded by file_loader)
    "job_description": Optional[str],
    "original_resume": Optional[str],
    
    # Processing pipeline outputs
    "job_strategy": Optional[str],          # job_analyzer → resume_screener
    "recruiter_feedback": Optional[str],    # resume_screener → resume_tailorer
    "tailored_resume": Optional[str],       # resume_tailorer → END
    
    # User interaction
    "messages": List,
    
    # Error handling
    "error": Optional[str]
}
```

### Key Benefits

- **🎯 Single Responsibility**: Each node has one clear purpose
- **📁 Centralized File I/O**: All file loading handled by dedicated node
- **📊 Clear Data Flow**: Easy to track what each node produces and consumes
- **🔧 Simple State**: Flat structure with documented field ownership
- **🏗️ Clean Organization**: Consistent naming and folder structure

## Processing Pipeline

```
START → file_loader → job_analyzer → resume_screener → resume_tailorer → END
```

### Node Responsibilities

1. **file_loader**: Loads job description and original resume from Supabase Storage
2. **job_analyzer**: Analyzes job posting to extract company strategy and requirements
3. **resume_screener**: Evaluates resume from recruiter perspective  
4. **resume_tailorer**: Tailors resume using analysis results, with user interaction if needed

## Clean File Structure

```
src/
├── state.py                    # Simplified flat state definition
├── graph.py                    # Main graph pipeline
├── test_graph.py              # Mock graph for frontend testing
├── nodes/                     # All processing nodes
│   ├── file_loader.py         # Centralized file I/O
│   │   └── screener.py        # Resume evaluation logic
│   └── resume_tailoring/
│       └── tailorer.py        # Resume customization logic
└── tools/                     # Shared utilities
```

### Naming Conventions

- **Folders**: Clear purpose (`job_analysis`, `resume_screening`, `resume_tailoring`)
- **Files**: Simple names (`analyzer.py`, `screener.py`, `tailorer.py`)  
- **Functions**: Verb-based (`job_analyzer`, `resume_screener`, `resume_tailorer`)

## Usage Examples

### Basic State Operations

```python
from src.state import create_initial_state, set_error

# Create initial state
state = create_initial_state("user_123", "job_456")

# Simple field updates (nodes return these)
update = {"job_strategy": "Strategic analysis complete"}
update = {"error": "Processing failed"}

# Helper functions
error_update = set_error("File not found")
clear_update = clear_error()
```

### Node Implementation Pattern

```python
async def your_node(state: GraphState, config: RunnableConfig) -> Dict[str, Any]:
    try:
        # Read required inputs
        user_id = state["user_id"]
        input_data = state["input_field"]
        
        if not input_data:
            return set_error("Required input missing")
        
        # Process data
        result = await process_data(input_data)
        
        # Return simple update
        return {"output_field": result}
        
    except Exception as e:
        return set_error(f"Processing failed: {str(e)}")
```

## Development Workflow

### Main Graph (Production)
```python
from src.graph import graph

# Execute with real AI processing
result = await graph.ainvoke({
    "user_id": "user_123",
    "job_id": "job_456",
    "messages": []
})
```

### Test Graph (Development)
```python
from src.test_graph import test_graph

# Execute with mock responses (no tokens used)
result = await test_graph.ainvoke({
    "user_id": "user_123", 
    "job_id": "job_456",
    "messages": []
})
```

## Error Handling

```python
# Check for errors in result
if result.get("error"):
    print(f"Processing failed: {result['error']}")
else:
    print(f"Success! Tailored resume: {result['tailored_resume']}")
```

## Key Improvements Made

### 🧹 **Cleaned Up Issues**

1. **Removed File I/O Pollution**: No more repeated file loading code in every node
2. **Simplified State**: Flat structure instead of over-engineered hierarchy  
3. **Better Naming**: Clear, consistent folder and file naming
4. **Separated Concerns**: Test graph moved to separate file
5. **Single Responsibility**: Each node has one clear job

### 📈 **Scalability**

- **Add New Nodes**: Follow simple pattern with clear input/output
- **Extend State**: Add fields with clear documentation of ownership
- **New File Types**: Extend file_loader node
- **Error Handling**: Standardized error patterns

## Future Extensions

The clean architecture makes it easy to add:

- **New Analysis Types**: Add nodes to the pipeline
- **Additional File Types**: Extend file_loader
- **Enhanced Interaction**: Extend user interaction patterns
- **Parallel Processing**: Split pipeline into parallel branches

The simplified structure scales naturally while maintaining clarity and maintainability.