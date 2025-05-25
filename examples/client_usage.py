"""
Example Client Usage

Shows how to handle GraphInterrupts from the info collection subgraph.

NOTE - the client must now handle responses from the Main Graph as well as conditionally handle responses from the Info Collection Subgraph.
"""

import asyncio
from langgraph.errors import GraphInterrupt
from src.graph import graph
from src.state import create_initial_state


async def example_client_usage():
    """
    Example of how a client handles the resume tailoring process with user interactions.

    The client doesn't need to know about subgraphs - GraphInterrupts bubble up
    and the client handles them the same way regardless of source.
    """

    # Create initial state
    state = create_initial_state(user_id="user123", job_id="job456")

    try:
        # Start the main graph
        print("Starting resume tailoring process...")
        result = await graph.ainvoke(state)

        # If we get here, no user interaction was needed
        print("Resume tailoring completed!")
        print(f"Tailored resume: {result['tailored_resume'][:100]}...")

    except GraphInterrupt as interrupt:
        print("User interaction needed...")

        # The interrupt contains the subgraph's state with conversation
        current_state = interrupt.value

        # Handle conversation loop
        while True:
            try:
                # Show the latest AI message to user
                if current_state.get("messages"):
                    latest_message = current_state["messages"][-1]
                    print(f"\nAI: {latest_message.content}")

                # Get user response (in real app, this would be from UI)
                user_input = input("\nYou: ")

                # Resume the graph with user input
                result = await graph.ainvoke(current_state, input=user_input)

                # If we get here, conversation is complete
                print("\nResume tailoring completed!")
                print(f"Tailored resume: {result['tailored_resume'][:100]}...")
                break

            except GraphInterrupt as next_interrupt:
                # More conversation needed
                current_state = next_interrupt.value
                continue


def simulate_user_responses():
    """
    Simulate user responses for testing.
    This would be replaced with actual UI interaction in a real application.
    """
    responses = [
        "I led a team of 5 developers on a React project that increased user engagement by 40%",
        "I have 3 years of experience with Python, Django, and PostgreSQL",
        "I managed the deployment pipeline using Docker and AWS, reducing deployment time by 60%",
    ]

    for i, response in enumerate(responses):
        print(f"Simulated user response {i+1}: {response}")
        yield response


if __name__ == "__main__":
    # Run the example
    asyncio.run(example_client_usage())
