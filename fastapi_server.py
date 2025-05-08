# This is the FastAPI server:
# To run this, use `uvicorn fastapi_server:app --reload`
# You can see the docs at `http://localhost:8000/docs`
# To test this, use `curl -X POST http://localhost:8000/chat/ -H "Content-Type: application/json" -d '{"query": "[your query here]"}'`

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from resume_tailoring_agent import process_query
from pydantic import BaseModel

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

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    ai_response: str

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
        from resume_tailoring_agent import MAX_HISTORY
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