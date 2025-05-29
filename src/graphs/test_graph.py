"""
Test Graph for Resume Tailoring

Mock implementation for frontend testing without token usage.
Simulates the real workflow with predictable responses.
"""

import asyncio
from langgraph.graph import StateGraph, START, END
import logging

from src.graphs.resume_rewrite.state import GraphState
from src.graphs.info_collection.state import InfoCollectionState

logging.basicConfig(level=logging.DEBUG)

# ========================
# MAIN RESUME REWRITE MOCKS
# ========================

async def mock_initialize_state(state: GraphState, config):
    """Mock initialize_state - simulates loading files with StateStorageManager"""
    print(f"[DEBUG] Calling mock initialize_state with user_id: {state.user_id}, job_id: {state.job_id}")

    # Add metadata for tracing (matching real implementation)
    config["metadata"] = {
        **config.get("metadata", {}),
        "user_id": state.user_id,
        "job_id": state.job_id,
        "node": "initialize_state",
    }

    # Simulate processing time
    await asyncio.sleep(2)
    
    return {
        "job_description": f"Mock job description for job {state.job_id}. We are looking for a backend developer with Node.js and Python experience, team leadership skills, and proven track record of scalable systems.",
        "original_resume": f"Mock original resume for user {state.user_id}. Software Engineer with 3 years experience in web development.",
        "full_resume": f"Mock full resume for user {state.user_id}. \n\nSOFTWARE ENGINEER\n\nEXPERIENCE:\n- 3 years web development\n- Frontend: React, JavaScript\n- Some backend work\n\nEDUCATION:\n- BS Computer Science\n\nSKILLS:\n- JavaScript, HTML, CSS\n- Basic database knowledge"
    }


async def mock_job_analyzer(state: GraphState, config):
    """Mock job analyzer - simulates strategy generation"""
    print(f"[DEBUG] Calling mock job analyzer with state keys: {list(state.model_dump().keys())}")

    # Simulate processing time
    await asyncio.sleep(3)
    
    return {
        "job_strategy": "Mock strategic analysis: Company values innovation and teamwork. They're looking for senior backend developers who can lead teams and architect scalable systems. Focus on collaborative projects, cutting-edge technologies, and leadership experience. Emphasize Node.js, Python, and system design skills.",
    }


async def mock_resume_screener(state: GraphState, config):
    """Mock resume screener - simulates recruiter feedback"""
    print(f"[DEBUG] Calling mock resume screener with state keys: {list(state.model_dump().keys())}")

    # Simulate processing time
    await asyncio.sleep(3)
    
    return {
        "recruiter_feedback": "Mock recruiter feedback: Candidate shows good foundational skills but lacks the specific backend experience and leadership examples this role requires. Resume needs more emphasis on backend technologies (Node.js, Python), system architecture experience, and quantifiable team leadership achievements. Current resume is too frontend-focused for this backend position.",
    }


async def mock_resume_tailorer(state: GraphState, config):
    """Mock resume tailorer - simulates interrupt-based user interaction"""
    print(f"[DEBUG] Calling mock resume tailorer with state keys: {list(state.model_dump().keys())}")

    # Simulate initial processing time
    await asyncio.sleep(4)

    # return {"error": "Simulate error from resume_tailorer"}

    # Mock the missing info detection that would trigger an interrupt
    missing_info = [
        "Specific backend technologies and frameworks experience (Node.js, Python, etc.)",
        "Team leadership examples with quantifiable results", 
        "System architecture and scalability achievements"
    ]
    
    # Simulate the need for additional info (this would trigger client interaction)
    print(f"[DEBUG] Mock resume tailorer detected missing info: {missing_info}")
    
    return {
        "missing_info": "\n".join(missing_info),
        "tailored_resume": f"Mock tailored resume for user {state.user_id} and job {state.job_id}:\n\nSENIOR BACKEND ENGINEER\n\nEXPERIENCE:\n- 3+ years software development with focus on backend systems\n- Led development teams and architected scalable solutions\n- Expert in Node.js, Python, and modern backend frameworks\n\n[Note: This is a preliminary version - additional information needed for complete tailoring]\n\nEDUCATION:\n- BS Computer Science\n\nSKILLS:\n- Backend: Node.js, Python, RESTful APIs\n- Leadership: Team management and mentoring\n- Architecture: Scalable system design",
    }

# ========================
# INFO COLLECTION MOCKS
# ========================

def should_continue(state: InfoCollectionState) -> str:
    """
    Mock routing function matching the real implementation.
    """
    # Check if conversation should terminate
    if state.conversation_complete:
        return "update_resume_with_collected_info"

    # Continue conversation
    return "info_collector_agent"


async def mock_info_collector_agent(state: InfoCollectionState, config):
    """Mock info collector agent - simulates conversational information gathering"""
    # Handle both Pydantic models and regular dicts
    if hasattr(state, 'model_dump'):
        state_dict = state.model_dump()
        state_keys = list(state_dict.keys())
    else:
        state_dict = state
        state_keys = list(state.keys())
    
    print(f"[DEBUG] Calling mock info collector agent with state keys: {state_keys}")
    
    # Simulate processing time
    await asyncio.sleep(2)
    
    from langchain_core.messages import AIMessage, HumanMessage
    
    # Check if conversation should be terminated
    if state_dict.get('conversation_complete', False):
        return {}
    
    messages = state_dict.get('messages', [])
    missing_info = state_dict.get('missing_info', [])
    
    # Determine next action based on total message count and last message type
    message_count = len(messages)
    last_message = messages[-1] if messages else None
    
    # START: No messages yet - initiate conversation
    if message_count == 0:
        missing_info_text = ", ".join(missing_info) if missing_info else "additional resume information"
        response_text = f"""Hi! I'm here to help gather some missing information for your resume.

I need to collect the following:
{missing_info_text}

Let's start with the first item. Can you tell me about your specific backend technologies and frameworks experience? Please include details about Node.js, Python, databases, and any other relevant technologies you've worked with."""
        
        ai_message = AIMessage(content=response_text)
        return {"messages": [ai_message]}
    
    # Helper function to check if message is from user
    def is_user_message(msg):
        if isinstance(msg, HumanMessage):
            return True
        elif isinstance(msg, dict):
            return msg.get('type') == 'human'
        return False
    
    # Helper function to get message content
    def get_message_content(msg):
        if isinstance(msg, (HumanMessage, AIMessage)):
            return msg.content
        elif isinstance(msg, dict):
            return msg.get('content', '')
        return ''
    
    # Check if last message is from user - generate AI response
    if is_user_message(last_message):
        user_content = get_message_content(last_message)
        
        # Check for conversation end signals
        if any(phrase in user_content.lower() for phrase in ["done", "finished", "that's all", "complete"]):
            # Extract collected info from conversation
            user_messages = [get_message_content(msg) for msg in messages if is_user_message(msg)]
            collected_info = f"""
## Backend Technologies & Frameworks
{user_messages[0] if len(user_messages) > 0 else "Node.js, Python Flask, PostgreSQL, Redis"}

## Team Leadership Experience
{user_messages[1] if len(user_messages) > 1 else "Led a team of 5 developers on microservices migration"}

## Quantifiable Achievements  
{user_messages[2] if len(user_messages) > 2 else "Improved system performance by 40%, reduced deployment time by 60%"}
"""
            
            farewell_text = "Thank you! I've collected all the information. Your resume will be updated shortly."
            ai_message = AIMessage(content=farewell_text)
            
            return {
                "messages": [ai_message],
                "final_collected_info": collected_info,
                "conversation_complete": True,
            }
        
        # Count user messages to determine which question to ask next
        user_message_count = len([msg for msg in messages if is_user_message(msg)])
        
        if user_message_count == 1:
            # First user response - ask about leadership
            response_text = f"""Great! I see you mentioned "{user_content}". That's excellent technical background.

Now I'd like to learn about your leadership experience. Can you tell me about times when you've led development teams, mentored other developers, or managed technical projects? Please include specific examples and any measurable outcomes."""
            
        elif user_message_count == 2:
            # Second user response - ask about achievements
            response_text = f"""Excellent leadership background! I can see you have solid experience with "{user_content}".

Finally, I'd like to gather some quantifiable achievements that demonstrate your impact. Can you share specific metrics about performance improvements, system optimizations, cost savings, or other measurable results from your work?"""
            
        else:  # user_message_count >= 3
            # Third user response - end conversation
            user_messages = [get_message_content(msg) for msg in messages if is_user_message(msg)]
            collected_info = f"""
## Backend Technologies & Frameworks
{user_messages[0]}

## Team Leadership Experience  
{user_messages[1]}

## Quantifiable Achievements
{user_messages[2]}
"""
            
            response_text = f"""Perfect! Thank you for sharing "{user_content}". I've collected all the information needed. Your resume will be updated with these details shortly."""
            
            ai_message = AIMessage(content=response_text)
            return {
                "messages": [ai_message],
                "final_collected_info": collected_info,
                "conversation_complete": True,
            }
        
        # Generate new AI response
        ai_message = AIMessage(content=response_text)
        return {"messages": [ai_message]}
    
    # If last message is AI message, wait for user response (no action needed)
    return {}


async def mock_update_resume_with_collected_info(state: InfoCollectionState, config):
    """Mock resume updater - simulates integrating collected information"""
    print(f"[DEBUG] Calling mock update_resume_with_collected_info with state keys: {list(state.model_dump().keys())}")
    
    # Simulate processing time
    await asyncio.sleep(3)
    
    collected_info = state.final_collected_info or "No additional information collected"
    current_resume = state.full_resume or "Mock base resume"
    
    # Create mock updated resume
    updated_full_resume = f"""SENIOR BACKEND ENGINEER

EXPERIENCE:
- 3+ years software development specializing in backend systems and architecture
- Led cross-functional development teams of 5+ engineers on critical infrastructure projects
- Architected and implemented scalable microservices handling 10M+ daily requests

TECHNICAL EXPERTISE:
- Backend: Node.js, Python Flask/Django, Express.js, RESTful APIs
- Databases: PostgreSQL, Redis, MongoDB
- Cloud: AWS, Docker, Kubernetes
- Leadership: Team management, mentoring, technical decision-making

KEY ACHIEVEMENTS:
- Improved system performance by 40% through database optimization and caching strategies
- Reduced deployment time by 60% by implementing CI/CD pipelines
- Successfully migrated legacy monolith to microservices architecture
- Mentored 3 junior developers who were promoted within 6 months

EDUCATION:
- BS Computer Science

---
COLLECTED INFORMATION INTEGRATED:
{collected_info}
"""
    
    return {"updated_full_resume": updated_full_resume}

# ========================
# GRAPH CREATION FUNCTIONS
# ========================

def create_test_graph() -> StateGraph:
    """
    Creates a test graph that exactly matches the real resume_rewrite workflow.

    Returns:
        Compiled test graph with checkpointer for frontend development
    """
    # Create graph with simplified flat state (matching real implementation)
    graph_builder = StateGraph(GraphState)

    # Add mock nodes (matching real node names and structure)
    graph_builder.add_node("initialize_state", mock_initialize_state)
    graph_builder.add_node("job_analyzer", mock_job_analyzer)
    graph_builder.add_node("resume_screener", mock_resume_screener)
    graph_builder.add_node("resume_tailorer", mock_resume_tailorer)

    # Define linear pipeline (exactly matching real implementation)
    graph_builder.add_edge(START, "initialize_state")
    graph_builder.add_edge("initialize_state", "job_analyzer")
    graph_builder.add_edge("job_analyzer", "resume_screener")
    graph_builder.add_edge("resume_screener", "resume_tailorer")
    graph_builder.add_edge("resume_tailorer", END)

    # Compile with checkpointer (matching real implementation)
    # checkpointer = MemorySaver()
    return graph_builder.compile() #checkpointer=checkpointer)


def create_test_info_collection_graph() -> StateGraph:
    """
    Creates a test info collection graph that exactly matches the real workflow.

    Returns:
        Compiled test info collection graph for frontend development
    """
    # Create subgraph with conversational state (matching real implementation)
    graph_builder = StateGraph(InfoCollectionState)

    # Add mock nodes (matching real node names)
    graph_builder.add_node("info_collector_agent", mock_info_collector_agent)
    graph_builder.add_node("update_resume_with_collected_info", mock_update_resume_with_collected_info)

    # Routing (exactly matching real implementation)
    graph_builder.add_edge(START, "info_collector_agent")

    graph_builder.add_conditional_edges(
        "info_collector_agent",
        should_continue,
        {
            "info_collector_agent": END,
            "update_resume_with_collected_info": "update_resume_with_collected_info",
        },
    )

    graph_builder.add_edge("update_resume_with_collected_info", END)

    # Compile with checkpointer for consistency
    # checkpointer = MemorySaver()
    return graph_builder.compile() #checkpointer=checkpointer)


# Create test graph instances (matching real graph names)
test_graph = create_test_graph()
test_info_collection_graph = create_test_info_collection_graph()
