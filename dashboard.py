"""
Dashboard for AI Employee Vault
Shows current status of all tasks
"""

import sys
from pathlib import Path
from datetime import datetime
import time

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent / "engine"))

from config import ensure_folders_exist
from engine.orchestrator import Orchestrator


def clear_screen():
    """Clear terminal screen"""
    import os
    os.system('cls' if os.name == 'nt' else 'clear')


def display_dashboard(orchestrator: Orchestrator):
    """Display the dashboard"""
    clear_screen()

    status = orchestrator.get_status()

    print("=" * 70)
    print(" " * 15 + "🤖 AI EMPLOYEE VAULT DASHBOARD")
    print("=" * 70)
    print()
    print(f"⏰ Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("-" * 70)
    print(f"  📥 Needs Action:        {status['needs_action']:>3} tasks")
    print(f"  ⏳ Pending Approval:    {status['pending_approval']:>3} tasks")
    print(f"  ✅ Approved (queued):   {status['approved']:>3} tasks")
    print(f"  ✔️  Done:                {status['done']:>3} tasks")
    print(f"  ❌ Rejected:            {status['rejected']:>3} tasks")
    print("-" * 70)
    print()

    # Show recent files
    print("📋 Recent Activity:")
    print()

    # Get most recent files from Done folder
    done_files = sorted(
        orchestrator.done_folder.glob("*.md"),
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )[:5]

    if done_files:
        print("  ✅ Last Completed:")
        for f in done_files:
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            print(f"    • {f.name} ({mtime.strftime('%H:%M:%S')})")
    else:
        print("  No completed tasks yet")

    print()
    print("=" * 70)
    print()
    print("Press Ctrl+C to exit")


def main():
    """Main dashboard loop"""
    try:
        # Ensure folders exist
        ensure_folders_exist()

        orchestrator = Orchestrator()

        while True:
            display_dashboard(orchestrator)
            time.sleep(2)  # Refresh every 2 seconds

    except KeyboardInterrupt:
        print("\n\n🛑 Exiting dashboard...")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
