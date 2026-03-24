"""
Facebook Comment Processor - BACKUP
Use this if orchestrator doesn't auto-process
"""

import re
from pathlib import Path
import sys
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from engine.logger import logger


class FacebookCommentProcessor:
    """Backup processor for Facebook comments"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.needs_action = self.base_dir / "Needs Action"
        self.pending_approval = self.base_dir / "Pending Approval"
        
        self.pending_approval.mkdir(exist_ok=True)
    
    def process_all_comments(self):
        """Process all Facebook comment tasks in Needs Action"""
        logger.info("🔍 Processing Facebook comments (backup mode)...")
        
        processed_count = 0
        for task_file in self.needs_action.glob("FACEBOOK_COMMENT_*.md"):
            # Check if already processed (file still exists)
            if task_file.exists():
                logger.info(f"⚠️  Manual processing needed: {task_file.name}")
                processed_count += 1
        
        if processed_count > 0:
            logger.info(f"⚠️  {processed_count} files need manual processing")
            logger.info("💡 Run: Claude Code → 'Process Facebook comments'")
        else:
            logger.info("✅ All Facebook comments processed automatically")


if __name__ == "__main__":
    processor = FacebookCommentProcessor()
    processor.process_all_comments()
