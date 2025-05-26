"""
Example usage of the updated user profile graph.

Demonstrates the three operation modes:
1. Direct resume update
2. LinkedIn profile parsing and merge
3. File parsing and merge
"""

import asyncio
from src.update_user_profile.graph import user_profile_update_graph
from src.update_user_profile.state import create_update_profile_state


async def example_direct_update():
    """Example: Direct resume update with new information"""
    print("=== Direct Resume Update Example ===")

    state = create_update_profile_state(
        user_id="test_user_001",
        operation_mode="update_resume",
        input_data="""
        ## New Experience
        
        **Senior Software Engineer** at TechCorp (2023-Present)
        - Led development of microservices architecture serving 1M+ users
        - Implemented CI/CD pipelines reducing deployment time by 60%
        - Mentored 3 junior developers and conducted code reviews
        
        ## New Skills
        - Kubernetes orchestration
        - GraphQL API design
        - Performance optimization
        """,
    )

    try:
        result = await user_profile_update_graph.ainvoke(state)
        print(f"✅ Update completed successfully")
        print(
            f"Updated resume length: {len(result.get('updated_full_resume', ''))} chars"
        )
        if result.get("error"):
            print(f"❌ Error: {result['error']}")
    except Exception as e:
        print(f"❌ Exception: {e}")


async def example_linkedin_parsing():
    """Example: LinkedIn profile parsing and merge"""
    print("\n=== LinkedIn Profile Parsing Example ===")

    state = create_update_profile_state(
        user_id="test_user_001",
        operation_mode="parse_linkedin",
        input_data="https://linkedin.com/in/example-profile",
    )

    try:
        result = await user_profile_update_graph.ainvoke(state)
        print(f"✅ LinkedIn parsing completed successfully")
        print(
            f"Updated resume length: {len(result.get('updated_full_resume', ''))} chars"
        )
        if result.get("error"):
            print(f"❌ Error: {result['error']}")
    except Exception as e:
        print(f"❌ Exception: {e}")


async def example_file_parsing():
    """Example: File parsing and merge"""
    print("\n=== File Parsing Example ===")

    state = create_update_profile_state(
        user_id="test_user_001",
        operation_mode="parse_file",
        input_data="resume_v2.pdf, cover_letter.txt",
    )

    try:
        result = await user_profile_update_graph.ainvoke(state)
        print(f"✅ File parsing completed successfully")
        print(
            f"Updated resume length: {len(result.get('updated_full_resume', ''))} chars"
        )
        if result.get("error"):
            print(f"❌ Error: {result['error']}")
    except Exception as e:
        print(f"❌ Exception: {e}")


async def main():
    """Run all examples"""
    print("Testing Updated User Profile Graph")
    print("=" * 50)

    await example_direct_update()
    await example_linkedin_parsing()
    await example_file_parsing()

    print("\n" + "=" * 50)
    print("All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())
