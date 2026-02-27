"""
File Watcher module
Monitors file system for new tasks dropped into Inbox
"""

import time
from pathlib import Path
from typing import List, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent
from .logger import logger


class FileWatcher(FileSystemEventHandler):
    def __init__(self, watch_path: Path, callback: Callable):
        self.watch_path = Path(watch_path)
        self.callback = callback
        self.observer = None

        # Ensure watch path exists
        self.watch_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"File watcher initialized for: {self.watch_path}")

    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        logger.info(f"New file detected: {file_path.name}")

        # Trigger callback
        try:
            self.callback(file_path)
        except Exception as e:
            logger.error(f"Error processing file {file_path.name}: {e}")

    def start(self):
        """Start watching the directory"""
        self.observer = Observer()
        self.observer.schedule(self, str(self.watch_path), recursive=False)
        self.observer.start()
        logger.info(f"File watcher started for: {self.watch_path}")

    def stop(self):
        """Stop watching the directory"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            logger.info("File watcher stopped")

    def scan_existing(self) -> List[Path]:
        """Scan for existing files in the watch directory"""
        files = [f for f in self.watch_path.iterdir() if f.is_file()]
        logger.info(f"Found {len(files)} existing file(s)")
        return files


def create_file_watcher(inbox_path: Path, callback: Callable) -> FileWatcher:
    """Factory function to create a file watcher"""
    return FileWatcher(inbox_path, callback)
