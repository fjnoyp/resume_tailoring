"""
Unified State Management Demo

Demonstrates the new StateStorageManager providing cohesive state operations
across different graph types, eliminating redundant data loaders.
"""

import asyncio
from src.tools.state_storage_manager import (
    StateStorageManager,
    StateLoadMode,
    load_resume_tailoring_data,
    load_user_profile_data,
    save_processing_result,
)


async def demo_resume_tailoring_state():
    """Demo: Resume tailoring state management"""
    print("=== Resume Tailoring State Management ===")

    user_id = "demo_user_001"
    job_id = "demo_job_001"

    # Load all required data for resume tailoring
    print(f"Loading resume tailoring data for {user_id}/{job_id}...")
    result = await load_resume_tailoring_data(user_id, job_id)

    if result.success:
        print(f"✅ Successfully loaded {len(result.loaded_fields)} fields:")
        for field, content in result.loaded_fields.items():
            print(f"  - {field}: {len(content)} chars")
    else:
        print(f"❌ Failed to load data: {result.error}")
        print(f"Missing files: {result.missing_files}")

    # Demo saving processing results
    print("\nSaving processing results...")
    success = await save_processing_result(
        user_id, job_id, "job_strategy", "Demo job strategy content with analysis..."
    )
    print(f"Job strategy saved: {'✅' if success else '❌'}")


async def demo_user_profile_state():
    """Demo: User profile state management"""
    print("\n=== User Profile State Management ===")

    user_id = "demo_user_001"

    # Load user profile data
    print(f"Loading user profile data for {user_id}...")
    result = await load_user_profile_data(user_id)

    if result.success:
        print(f"✅ Successfully loaded {len(result.loaded_fields)} fields:")
        for field, content in result.loaded_fields.items():
            print(f"  - {field}: {len(content)} chars")
    else:
        print(f"❌ Failed to load data: {result.error}")

    # Demo saving updated resume
    print("\nSaving updated resume...")
    success = await save_processing_result(
        user_id,
        None,
        "updated_full_resume",
        "Demo updated resume content with new information...",
    )
    print(f"Updated resume saved: {'✅' if success else '❌'}")


async def demo_advanced_state_operations():
    """Demo: Advanced state operations"""
    print("\n=== Advanced State Operations ===")

    user_id = "demo_user_001"
    job_id = "demo_job_001"

    # Load specific mode data
    print("Loading cover letter mode data...")
    result = await StateStorageManager.load_state_data(
        user_id, job_id, StateLoadMode.COVER_LETTER
    )

    if result.success:
        print(f"✅ Cover letter data loaded: {list(result.loaded_fields.keys())}")
    else:
        print(f"❌ Cover letter data failed: {result.error}")

    # Save multiple fields at once
    print("\nSaving multiple fields...")
    fields_to_save = {
        "recruiter_feedback": "Demo recruiter feedback content...",
        "tailored_resume": "Demo tailored resume content...",
    }

    save_results = await StateStorageManager.save_multiple_fields(
        user_id, job_id, fields_to_save
    )

    for field, success in save_results.items():
        print(f"  {field}: {'✅' if success else '❌'}")


async def demo_state_cohesion():
    """Demo: State cohesion and visibility"""
    print("\n=== State Cohesion Demo ===")

    print("🔍 State Management Benefits:")
    print("  ✅ Single source of truth for all file operations")
    print("  ✅ Consistent error handling across all graphs")
    print("  ✅ Clear visibility into what data is loaded/saved")
    print("  ✅ Type-safe field mappings prevent path errors")
    print("  ✅ Mode-based loading for different graph types")
    print("  ✅ Unified logging and debugging")

    print("\n📊 Eliminated Redundancy:")
    print("  ❌ No more duplicate data_loader nodes")
    print("  ❌ No more scattered file I/O logic")
    print("  ❌ No more inconsistent error patterns")
    print("  ❌ No more magic string file paths")

    print("\n🎯 Cohesive State View:")
    print("  📁 All file operations go through StateStorageManager")
    print("  🔄 Consistent load/save patterns across graphs")
    print("  🎛️ Centralized configuration for different modes")
    print("  📝 Clear audit trail of state changes")


async def main():
    """Run all state management demos"""
    print("🚀 Unified State Management System Demo")
    print("=" * 60)

    await demo_resume_tailoring_state()
    await demo_user_profile_state()
    await demo_advanced_state_operations()
    await demo_state_cohesion()

    print("\n" + "=" * 60)
    print("✨ State management system provides cohesive operations!")


if __name__ == "__main__":
    asyncio.run(main())
