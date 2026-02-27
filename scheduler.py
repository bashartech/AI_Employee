"""
Scheduler - Gold Tier Implementation
Handles scheduled tasks like CEO Weekly Briefing
"""

import schedule
import time
from pathlib import Path
from datetime import datetime
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from engine.ceo_briefing import generate_ceo_briefing
from engine.audit_logger import log_action

VAULT = Path(__file__).parent


def run_ceo_briefing():
    """Generate CEO weekly briefing"""
    print("\n" + "="*60)
    print("📊 GENERATING CEO WEEKLY BRIEFING")
    print("="*60)
    
    try:
        briefing_file = generate_ceo_briefing()
        if briefing_file:
            print(f"\n✅ Briefing generated successfully!")
            print(f"📄 Location: {briefing_file}")
            log_action("SCHEDULER_CEO_BRIEFING", {"status": "success", "file": str(briefing_file)})
        else:
            print("\n❌ Failed to generate briefing")
            log_action("SCHEDULER_CEO_BRIEFING", {"status": "failed", "error": "No file generated"})
    except Exception as e:
        print(f"\n❌ Error: {e}")
        log_action("SCHEDULER_CEO_BRIEFING", {"status": "failed", "error": str(e)})


def run_scheduler():
    """Main scheduler loop"""
    print("\n" + "="*60)
    print("🕐 AI EMPLOYEE SCHEDULER STARTED")
    print("="*60)
    print(f"Vault: {VAULT}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📋 Scheduled Tasks:")
    print("  - Every Monday at 08:00 AM: Generate CEO Weekly Briefing")
    print("\nPress Ctrl+C to stop\n")
    
    # Schedule CEO briefing - Every Monday at 8:00 AM
    schedule.every().monday.at("08:00").do(run_ceo_briefing)
    
    # For testing: Run briefing every minute (uncomment for testing only!)
    # schedule.every(1).minutes.do(run_ceo_briefing)
    
    log_action("SCHEDULER_START", {"status": "started"})
    
    # Run scheduler loop
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n\n⏹ Scheduler stopped by user")
            log_action("SCHEDULER_STOP", {"status": "stopped"})
            break
        except Exception as e:
            print(f"❌ Scheduler error: {e}")
            log_action("SCHEDULER_ERROR", {"status": "error", "error": str(e)})
            time.sleep(60)


if __name__ == "__main__":
    run_scheduler()
