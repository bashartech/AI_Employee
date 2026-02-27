"""
Main entry point for AI Employee Vault automation
Runs the Claude Code-powered orchestrator
"""

import sys
from pathlib import Path

# Add engine to path

sys.path.insert(0, str(Path(__file__).parent / "engine"))

from config import ensure_folders_exist
from engine.orchestrator import Orchestrator
from engine.logger import logger


def main():
    """Main entry point"""
    print("=" * 60)
    print("🤖 AI EMPLOYEE VAULT - CLAUDE CODE AUTOMATION")
    print("=" * 60)
    print()
    print("Starting automation engine...")
    print()
    print("Folders being monitored:")
    print("  📥 Needs Action: New tasks appear here")
    print("  ⏳ Pending Approval: Tasks requiring human approval")
    print("  ✅ Approved: Move approved tasks here")
    print("  ✔️  Done: Completed tasks")
    print("  ❌ Rejected: Rejected tasks")
    print()
    print("How it works:")
    print("  1. Watchers create tasks in 'Needs Action/'")
    print("  2. Claude Code processes them → 'Pending Approval/'")
    print("  3. You review and move to 'Approved/'")
    print("  4. execute_approved.py executes them → 'Done/'")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    try:
        # Ensure folders exist (centralized)
        ensure_folders_exist()

        # Initialize and start orchestrator
        orchestrator = Orchestrator()

        # Show initial status
        status = orchestrator.get_status()
        print(f"Initial Status:")
        print(f"  📥 Needs Action: {status['needs_action']}")
        print(f"  ⏳ Pending Approval: {status['pending_approval']}")
        print(f"  ✅ Approved: {status['approved']}")
        print(f"  ✔️  Done: {status['done']}")
        print(f"  ❌ Rejected: {status['rejected']}")
        print()

        # Start the orchestrator
        orchestrator.start()

    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down gracefully...")
        logger.info("Shutdown requested by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
