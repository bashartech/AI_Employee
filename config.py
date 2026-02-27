"""
Configuration module
Centralized configuration for all scripts
"""

from pathlib import Path
import os

# Base directory - the vault root
BASE_DIR = Path(__file__).parent

# Folder structure (shared across all scripts)
NEEDS_ACTION_FOLDER = BASE_DIR / "Needs Action"
PENDING_APPROVAL_FOLDER = BASE_DIR / "Pending Approval"
APPROVED_FOLDER = BASE_DIR / "Approved"
DONE_FOLDER = BASE_DIR / "Done"
REJECTED_FOLDER = BASE_DIR / "Rejected"

# Qwen/Ollama configuration
QWEN_MODEL = os.getenv('QWEN_MODEL', 'qwen2.5:latest')

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')


def ensure_folders_exist():
    """Create all required folders if they don't exist"""
    folders = [
        NEEDS_ACTION_FOLDER,
        PENDING_APPROVAL_FOLDER,
        APPROVED_FOLDER,
        DONE_FOLDER,
        REJECTED_FOLDER
    ]

    for folder in folders:
        folder.mkdir(exist_ok=True)
