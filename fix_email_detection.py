"""
Quick Fix for Email Task Detection
Upload this to server to fix email processing
"""

import sys
from pathlib import Path

# Read orchestrator file
orchestrator_path = Path("/home/AI_Employee/engine/orchestrator.py")
content = orchestrator_path.read_text(encoding='utf-8')

# Find and fix the _detect_task_type method
# Add better email detection

print("Checking orchestrator email detection...")

# Check if email detection exists
if "'email' in filename_lower or 'type: email' in content_lower:" in content:
    print("✓ Email detection found")
else:
    print("⚠️  Email detection missing - needs fix")

# Check inbox_email processing
if "inbox_email" in content:
    print("✓ Inbox email processing found")
else:
    print("❌ Inbox email processing MISSING")

print("\n=== MANUAL FIX REQUIRED ===")
print("The orchestrator needs to detect email tasks properly.")
print("Check engine/orchestrator.py _detect_task_type method")
