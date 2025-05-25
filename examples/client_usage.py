"""
Example Client Usage

Shows how to handle GraphInterrupts from the info collection subgraph.

The info collection subgraph automatically updates the user's full resume file
when collecting missing information, ensuring future sessions benefit from
the collected data while the current session uses it immediately.
"""

import asyncio
from langgraph.errors import GraphInterrupt
from src.graph import graph
from src.state import create_initial_state


async def example_client_usage():
    """
    Example of how a client handles the resume tailoring process with user interactions.

    Key points:
    - Client only interacts with main graph (subgraph is transparent)
    - GraphInterrupts bubble up from info collection subgraph
    - Full resume updates happen automatically during info collection
    - Current session gets immediate benefit of collected information
    - Future sessions automatically have access to updated full resume
    """

    # Create initial state
    state = create_initial_state(user_id="user123", job_id="job456")

    try:
        # Start the main graph
        print("🚀 Starting resume tailoring process...")
        result = await graph.ainvoke(state)

        # If we get here, no user interaction was needed
        print("✅ Resume tailoring completed without additional info needed!")
        print(f"📄 Tailored resume preview: {result['tailored_resume'][:100]}...")

    except GraphInterrupt as interrupt:
        print("💬 Additional information needed from user...")
        print("📝 Starting conversation to collect missing details...")

        # The interrupt contains the subgraph's state with conversation
        current_state = interrupt.value

        # Handle conversation loop
        conversation_count = 0
        while True:
            try:
                # Show the latest AI message to user
                if current_state.get("messages"):
                    latest_message = current_state["messages"][-1]
                    print(f"\n🤖 AI: {latest_message.content}")

                # Get user response (in real app, this would be from UI)
                user_input = input("\n👤 You: ")
                conversation_count += 1

                # Resume the graph with user input
                result = await graph.ainvoke(current_state, input=user_input)

                # If we get here, conversation is complete
                print(
                    f"\n✅ Resume tailoring completed after {conversation_count} interactions!"
                )
                print(
                    "💾 Your full resume has been automatically updated with the new information."
                )
                print(
                    "🎯 Future job applications will benefit from this collected data."
                )
                print(
                    f"📄 Tailored resume preview: {result['tailored_resume'][:100]}..."
                )
                break

            except GraphInterrupt as next_interrupt:
                # More conversation needed
                current_state = next_interrupt.value
                continue


async def example_with_simulated_responses():
    """
    Example with simulated user responses for testing.
    Shows how the system handles multiple questions and updates.
    """
    print("🧪 Running simulation with predefined responses...")

    # Simulated responses
    responses = [
        "I led a team of 5 developers on a React project that increased user engagement by 40% over 6 months",
        "I have 3 years of experience with Python, Django, and PostgreSQL, including building APIs for 50k+ users",
        "I managed the CI/CD pipeline using Docker and AWS, reducing deployment time from 2 hours to 15 minutes",
    ]

    response_index = 0
    state = create_initial_state(user_id="user123", job_id="job456")

    try:
        result = await graph.ainvoke(state)
        print("✅ No additional info needed!")

    except GraphInterrupt as interrupt:
        current_state = interrupt.value

        while True:
            try:
                if current_state.get("messages"):
                    latest_message = current_state["messages"][-1]
                    print(f"\n🤖 AI: {latest_message.content}")

                # Use simulated response
                if response_index < len(responses):
                    user_input = responses[response_index]
                    print(f"\n👤 Simulated Response: {user_input}")
                    response_index += 1
                else:
                    user_input = "I don't have any additional information to add."
                    print(f"\n👤 Simulated Response: {user_input}")

                result = await graph.ainvoke(current_state, input=user_input)

                print(f"\n✅ Simulation completed!")
                print(
                    "💾 Full resume automatically updated with collected information."
                )
                break

            except GraphInterrupt as next_interrupt:
                current_state = next_interrupt.value
                continue


if __name__ == "__main__":
    print("Choose example to run:")
    print("1. Interactive example (requires user input)")
    print("2. Simulated example (automated responses)")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        asyncio.run(example_client_usage())
    elif choice == "2":
        asyncio.run(example_with_simulated_responses())
    else:
        print("Invalid choice. Running interactive example...")
        asyncio.run(example_client_usage())
