from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
import asyncio
from langgraph.prebuilt import create_react_agent
from resume_tailoring_tools import resume_tailoring_tools
from user_experience_gathering_tools import user_experience_gathering_tools

# Load environment variables
load_dotenv()

# Initialize the model
model = ChatAnthropic(
    model_name="claude-3-7-sonnet-latest",
    timeout=120,
    stop=None
)

agent = create_react_agent(model, [*resume_tailoring_tools, *user_experience_gathering_tools])

async def process_query(query: list, debug: bool = False):
    if debug:
        print("[DEBUG] process_query called with query:", query)

    agent_response = await agent.ainvoke({"messages": query})

    if debug:
        print("[DEBUG] agent_response:", agent_response)

    return agent_response['messages'][-1].content

MAX_HISTORY = 20  # or whatever fits your model's context window

async def chat_loop():
    print("Type your queries or 'quit' to exit.")
    conversation = []  # This will store the conversation history

    while True:
        try:
            query = input("\nQuery: ").strip()
            if query.lower() == 'quit':
                break

            conversation.append({"role": "user", "content": query})
            if len(conversation) > MAX_HISTORY:
                conversation = conversation[-MAX_HISTORY:]

            ai_reply = await process_query(conversation)

            print("\nAI response:\n", ai_reply)
            conversation.append({"role": "assistant", "content": ai_reply})

        except Exception as e:
            print(f"\nError: {str(e)}")

async def main():
    await chat_loop()

if __name__ == "__main__":
    asyncio.run(main())