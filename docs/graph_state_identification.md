# Graph State Identification System

## Overview

The resume tailoring system now includes a unified state identification system that allows clients to easily determine which graph state schema they're receiving and handle different state types appropriately.

## State Types

All graph states now include a `graph_type` field that identifies the state schema:

### 1. Resume Rewrite State (`"resume_rewrite"`)
- **Purpose**: Main resume tailoring pipeline
- **Key Fields**: `tailored_resume`, `job_strategy`, `recruiter_feedback`
- **Usage**: Primary workflow for generating tailored resumes

### 2. Info Collection State (`"info_collection"`)
- **Purpose**: Interactive conversation to collect missing resume information
- **Key Fields**: `messages`, `final_collected_info`, `is_complete`
- **Usage**: Subgraph for gathering additional user details

### 3. Update User Profile State (`"update_user_profile"`)
- **Purpose**: Update user's full resume with new information
- **Key Fields**: `updated_full_resume`, `operation_mode`, `parsed_content`
- **Usage**: Subgraph for profile updates (LinkedIn, files, direct input)

## Client Integration

### Using the State Utils Module

```python
from src.graphs.state_utils import (
    get_state_type,
    is_resume_rewrite_state,
    is_info_collection_state,
    has_conversation_messages,
    get_completion_status,
    format_state_summary
)

def handle_graph_result(state):
    """Handle any graph state result with type identification."""
    
    # Identify the state type
    state_type = get_state_type(state)
    print(f"Received {state_type} state")
    
    # Handle based on type
    if is_resume_rewrite_state(state):
        completion = get_completion_status(state)
        if completion['is_complete']:
            resume = state['tailored_resume']
            print(f"✓ Resume generated: {len(resume)} chars")
    
    elif is_info_collection_state(state):
        if has_conversation_messages(state):
            messages = state['messages']
            if messages:
                # Show AI message to user
                ai_message = messages[-1].content
                print(f"AI: {ai_message}")
                # Get user response and continue conversation
    
    # Print detailed summary
    print(format_state_summary(state))
```

### Direct State Type Checking

```python
def process_graph_state(state):
    """Process state based on graph_type field."""
    
    graph_type = state.get('graph_type')
    
    if graph_type == 'resume_rewrite':
        # Handle main resume tailoring result
        if state.get('tailored_resume'):
            save_tailored_resume(state['tailored_resume'])
    
    elif graph_type == 'info_collection':
        # Handle conversation state
        if state.get('messages'):
            display_conversation(state['messages'])
        if state.get('is_complete'):
            process_collected_info(state['final_collected_info'])
    
    elif graph_type == 'update_user_profile':
        # Handle profile update result
        if state.get('updated_full_resume'):
            update_user_profile(state['updated_full_resume'])
    
    else:
        raise ValueError(f"Unknown graph_type: {graph_type}")
```

## State Schema Reference

### Resume Rewrite State Schema
```python
{
    "graph_type": "resume_rewrite",
    "user_id": str,
    "job_id": str,
    "job_description": Optional[str],
    "original_resume": Optional[str],
    "full_resume": Optional[str],
    "job_strategy": Optional[str],
    "recruiter_feedback": Optional[str],
    "tailored_resume": Optional[str],  # Main output
    "error": Optional[str]
}
```

### Info Collection State Schema
```python
{
    "graph_type": "info_collection",
    "missing_info_requirements": str,
    "user_id": str,
    "full_resume": str,
    "messages": List[Message],  # Conversation history
    "collected_info": Dict[str, Any],
    "remaining_questions": List[str],
    "final_collected_info": Optional[str],  # Main output
    "updated_full_resume": Optional[str],
    "is_complete": bool,
    "error": Optional[str]
}
```

### Update User Profile State Schema
```python
{
    "graph_type": "update_user_profile",
    "user_id": str,
    "operation_mode": str,  # "update_resume", "parse_linkedin", "parse_file"
    "input_data": str,
    "current_full_resume": Optional[str],
    "updated_full_resume": Optional[str],  # Main output
    "parsed_content": Optional[str],
    "error": Optional[str]
}
```

## Error Handling

All state types include an `error` field for consistent error handling:

```python
from src.graphs.state_utils import has_error, get_error_message

def safe_process_state(state):
    """Safely process any state with error handling."""
    
    if has_error(state):
        error_msg = get_error_message(state)
        print(f"Graph execution failed: {error_msg}")
        return False
    
    # Process successful state
    state_type = get_state_type(state)
    # ... handle based on type
    return True
```

## Conversation Handling

Only info collection states have conversation messages. Use the utility functions to check:

```python
from src.graphs.state_utils import has_conversation_messages

def handle_conversation(state):
    """Handle conversation states specifically."""
    
    if not has_conversation_messages(state):
        return  # Not a conversation state
    
    messages = state['messages']
    if not messages:
        return  # No messages yet
    
    last_message = messages[-1]
    
    # Display AI message to user
    print(f"AI: {last_message.content}")
    
    # Get user response
    user_response = input("You: ")
    
    # Continue conversation by adding user message and re-invoking graph
    from langchain_core.messages import HumanMessage
    updated_state = {
        **state,
        "messages": messages + [HumanMessage(content=user_response)]
    }
    
    return updated_state
```

## Benefits

### 1. **Type Safety**
- Clear identification of state schemas
- Prevents runtime errors from accessing wrong fields
- Better IDE support and autocomplete

### 2. **Unified Client Interface**
- Single set of utility functions for all state types
- Consistent error handling across all graphs
- Simplified client code

### 3. **Future Extensibility**
- Easy to add new graph types
- Backward compatible state identification
- Centralized state handling logic

### 4. **Better Debugging**
- Clear state summaries for logging
- Easy identification of state flow issues
- Consistent error reporting

## Migration Guide

### For Existing Clients

1. **Update State Handling**: Use `get_state_type()` instead of checking specific fields
2. **Add Error Checking**: Use `has_error()` and `get_error_message()` for consistent error handling
3. **Use Utility Functions**: Replace custom state checking with provided utilities
4. **Handle New Fields**: All states now have `graph_type` field

### Example Migration

**Before:**
```python
def handle_result(state):
    if 'tailored_resume' in state:
        # Handle resume result
        pass
    elif 'messages' in state:
        # Handle conversation
        pass
```

**After:**
```python
def handle_result(state):
    if is_resume_rewrite_state(state):
        # Handle resume result
        pass
    elif is_info_collection_state(state):
        # Handle conversation
        pass
```

## Testing

The state utils module includes comprehensive type checking and validation:

```python
from src.graphs.state_utils import get_state_type

# Test state identification
test_states = [
    {"graph_type": "resume_rewrite", "user_id": "123"},
    {"graph_type": "info_collection", "user_id": "123"},
    {"graph_type": "update_user_profile", "user_id": "123"}
]

for state in test_states:
    state_type = get_state_type(state)
    print(f"State type: {state_type}")
``` 