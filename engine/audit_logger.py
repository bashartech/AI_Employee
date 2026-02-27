"""
Audit Logger - Gold Tier Implementation
Logs all AI Employee actions for compliance and debugging
"""

import logging
from pathlib import Path
from datetime import datetime
import json

# Setup logging
LOG_FOLDER = Path(__file__).parent.parent / "Logs"
LOG_FOLDER.mkdir(exist_ok=True)

# Daily audit log file
LOG_FILE = LOG_FOLDER / f"audit_{datetime.now().strftime('%Y-%m-%d')}.log"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("AIEmployeeVault")


def log_action(action_type: str, details: dict, status: str = "success"):
    """
    Log an action to the audit log
    
    Args:
        action_type: Type of action (e.g., "ODOO_CREATE_LEAD")
        details: Dictionary of action details
        status: "success" or "failed"
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action_type": action_type,
        "status": status,
        "details": details
    }
    
    if status == "success":
        logger.info(json.dumps(log_entry))
    else:
        logger.error(json.dumps(log_entry))


def get_today_audit_log():
    """Read today's audit log"""
    if LOG_FILE.exists():
        return LOG_FILE.read_text(encoding='utf-8')
    return ""


def get_actions_by_type(action_type: str):
    """Get all actions of a specific type from today's log"""
    if not LOG_FILE.exists():
        return []
    
    actions = []
    with open(LOG_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if action_type in line:
                try:
                    # Extract JSON part from log line
                    json_str = line.split(' - ', 3)[-1]
                    actions.append(json.loads(json_str))
                except:
                    continue
    return actions


# Test the logger
if __name__ == "__main__":
    print("Testing Audit Logger...")
    log_action("TEST_ACTION", {"message": "This is a test", "user": "admin"})
    print(f"✅ Log entry created. Check: {LOG_FILE}")
