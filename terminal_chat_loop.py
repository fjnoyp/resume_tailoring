# This is the chat loop for terminal running tests:
# To run this, use `uv run terminal_chat_loop.py`

import asyncio
from resume_tailoring_agent import MAX_HISTORY, process_query


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