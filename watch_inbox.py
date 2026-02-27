"""
Inbox Watcher
Monitors Inbox folder and moves files to Needs Action folder
"""

import sys
import time
from pathlib import Path
from datetime import datetime
import shutil

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from config import NEEDS_ACTION_FOLDER, ensure_folders_exist
from engine.watcher_file import FileWatcher
from engine.logger import logger


class InboxWatcher:
    """Watches Inbox folder and processes new files"""

    def __init__(self):
        """Initialize inbox watcher"""
        # Create folders
        ensure_folders_exist()

        # Inbox folder
        self.inbox_folder = Path.cwd() / "Inbox"
        self.inbox_folder.mkdir(exist_ok=True)

        logger.info("✅ Inbox watcher initialized")

    def process_file(self, file_path: Path):
        """
        Process a file from Inbox and move to Needs Action

        Args:
            file_path: Path to the file in Inbox
        """
        try:
            logger.info(f"📥 Processing file: {file_path.name}")

            # Read file content
            if file_path.suffix.lower() in ['.md', '.txt']:
                content = file_path.read_text(encoding='utf-8')
            else:
                content = f"File: {file_path.name}\nType: {file_path.suffix}"

            # Create task file in Needs Action
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            task_filename = f"INBOX_{file_path.stem}_{timestamp}.md"

            task_content = f"""# Task from Inbox: {file_path.name}

**Source:** Inbox folder
**Original File:** {file_path.name}
**Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Type:** File Drop

## Content

{content}

## Suggested Actions

- [ ] Review the content
- [ ] Take appropriate action
- [ ] Mark as complete when done

## Notes

Add your notes here...
"""

            # Save to Needs Action
            task_path = NEEDS_ACTION_FOLDER / task_filename
            task_path.write_text(task_content, encoding='utf-8')

            logger.info(f"✅ Created task: {task_filename}")

            # Move original file to archive or delete
            archive_folder = self.inbox_folder / "Processed"
            archive_folder.mkdir(exist_ok=True)

            archive_path = archive_folder / file_path.name
            shutil.move(str(file_path), str(archive_path))

            logger.info(f"📦 Archived original file: {file_path.name}")

        except Exception as e:
            logger.error(f"❌ Error processing file {file_path.name}: {e}")

    def start(self):
        """Start monitoring Inbox folder"""
        logger.info("👀 Starting Inbox watcher...")
        logger.info(f"📂 Monitoring: {self.inbox_folder}")
        logger.info(f"📤 Output to: {NEEDS_ACTION_FOLDER}")
        logger.info("Press Ctrl+C to stop")
        print()
        print("=" * 60)
        print("📥 INBOX WATCHER STARTED")
        print("=" * 60)
        print()
        print(f"Monitoring: {self.inbox_folder}")
        print(f"Output to: Needs Action/")
        print()
        print("Drop files into the Inbox folder to process them.")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        print()

        # Create file watcher
        watcher = FileWatcher(self.inbox_folder, self.process_file)

        # Process existing files first
        existing_files = watcher.scan_existing()
        if existing_files:
            logger.info(f"📋 Processing {len(existing_files)} existing files...")
            for file_path in existing_files:
                self.process_file(file_path)

        # Start watching
        watcher.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Stopping Inbox watcher...")
            watcher.stop()
            print()
            print("=" * 60)
            print("✅ INBOX WATCHER STOPPED")
            print("=" * 60)


if __name__ == "__main__":
    watcher = InboxWatcher()
    watcher.start()
