# This is the FastAPI server:
# To run this, use `uvicorn fastapi_server:app --reload`
# You can see the docs at `http://localhost:8000/docs`
# To test this, use `curl -X POST http://localhost:8000/chat/ -H "Content-Type: application/json" -d '{"query": "[your query here]"}'`

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from resume_tailoring_agent import process_query, MAX_HISTORY
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse
import asyncio
import json
from resume_tailoring_agent import process_query_stream, to_serializable

# Initialize FastAPI client
app = FastAPI()

# Allow all origins (for development)
# For production, replace allow_origins=["*"] with a list of allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allows all headers
)

conversation = []  # This will store the conversation history
running_tasks = {}

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    ai_response: str

def conversation_to_dicts(conversation):
    result = []
    for msg in conversation:
        if hasattr(msg, "content") and hasattr(msg, "type"):
            role = getattr(msg, "role", None) or getattr(msg, "type", "user")
            result.append({"role": role, "content": msg.content})
        elif isinstance(msg, dict):
            result.append(msg)
        else:
            result.append({"role": "system", "content": str(msg)})
    return result

@app.post("/chat/stream")
async def chat_stream(request: Request, chat_request: ChatRequest):
    conversation.append({"role": "user", "content": chat_request.query})
    if len(conversation) > MAX_HISTORY:
        conversation[:] = conversation[-MAX_HISTORY:]

    safe_conversation = conversation_to_dicts(conversation)

    async def event_generator():
        async for step in process_query_stream(safe_conversation):
            yield {
                "event": "message",
                "data": json.dumps(to_serializable(step))
            }
    return EventSourceResponse(event_generator())

# This is the FastAPI server:
@app.post("/chat/", response_model=ChatResponse) # This line decorates 'chat' as a POST endpoint
async def chat_request(request: ChatRequest):
    try:
        user_message = request.query
        if not user_message:
            raise HTTPException(status_code=400, detail="Missing 'query' in request.")

        # Add user message to conversation
        conversation.append({"role": "user", "content": user_message})

        # Trim conversation to MAX_HISTORY
        if len(conversation) > MAX_HISTORY:
            conversation[:] = conversation[-MAX_HISTORY:]

        # Get AI response
        ai_response = await process_query(conversation)

        # Add AI response to conversation
        conversation.append({"role": "assistant", "content": ai_response})

        # Return the ai response
        return ChatResponse(ai_response=ai_response)
    except Exception as e:
        # Handle exceptions or errors
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("shutdown")
async def shutdown_event():
    print("Shutting down, cancelling all running tasks...")
    # Cancel all running tasks
    for session_id, task in list(running_tasks.items()):
        print(f"Cancelling task {session_id}")
        task.cancel()
    # Optionally, wait for all tasks to finish
    await asyncio.gather(*running_tasks.values(), return_exceptions=True)
    print("All tasks cancelled.")