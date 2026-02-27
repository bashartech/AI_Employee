"""
AI Employee Vault Engine Package
"""

from engine.logger import logger
from .ai_client import AIClient
from .processor import TaskProcessor
from .watcher_file import FileWatcher
from .watcher_gmail import GmailWatcher
from .watcher_whatsapp import WhatsAppWatcher
from .watcher_linkedin import LinkedInWatcher
from .scheduler import Scheduler, SCHEDULE_PRESETS
from .approval_manager import ApprovalManager
from .reasoning_loop import ReasoningLoop

__version__ = "0.1.0"
__all__ = [
    "logger",
    "AIClient",
    "TaskProcessor",
    "FileWatcher",
    "GmailWatcher",
    "WhatsAppWatcher",
    "LinkedInWatcher",
    "Scheduler",
    "SCHEDULE_PRESETS",
    "ApprovalManager",
    "ReasoningLoop",
]
