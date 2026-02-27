"""
Task Processor module
Handles task creation, analysis, and completion workflow
"""

import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from engine.logger import logger
from engine.ai_client import AIClient


class TaskProcessor:
    def __init__(self, base_path: Path, ai_client: Optional[AIClient] = None):
        self.base_path = Path(base_path)
        self.inbox = self.base_path / "Inbox"
        self.needs_action = self.base_path / "Needs_Action"
        self.done = self.base_path / "Done"
        self.dashboard = self.base_path / "Dashboard.md"

        self.ai_client = ai_client or AIClient()

        # Ensure directories exist
        self.inbox.mkdir(exist_ok=True)
        self.needs_action.mkdir(exist_ok=True)
        self.done.mkdir(exist_ok=True)

        logger.info("Task processor initialized")

    def create_task_from_file(self, file_path: Path) -> Path:
        """Create a task file from a dropped file"""
        task_name = f"TASK_{file_path.stem}.md"
        task_path = self.needs_action / task_name

        task_content = f"""---
type: file_drop
original_file: {file_path.name}
status: pending
created: {datetime.now().isoformat()}
---

# New Task

A new file was dropped: {file_path.name}

Please analyze and summarize it.
"""

        task_path.write_text(task_content, encoding='utf-8')
        logger.info(f"Created task: {task_name}")

        return task_path

    def create_task_from_message(self, message_data: Dict[str, Any], source: str) -> Path:
        """Create a task file from a message (email, WhatsApp, LinkedIn)"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        task_name = f"TASK_{source}_{timestamp}.md"
        task_path = self.needs_action / task_name

        task_content = f"""---
type: {source}_message
status: pending
created: {datetime.now().isoformat()}
from: {message_data.get('from', 'Unknown')}
---

# New Task from {source.title()}

**From:** {message_data.get('from', 'Unknown')}
**Subject:** {message_data.get('subject', 'N/A')}

## Message Content

{message_data.get('body', message_data.get('content', ''))}

---

Please analyze and respond to this message.
"""

        task_path.write_text(task_content, encoding='utf-8')
        logger.info(f"Created task from {source}: {task_name}")

        return task_path

    def process_task(self, task_path: Path) -> bool:
        """Process a task using AI"""
        try:
            # Read task file
            content = task_path.read_text(encoding='utf-8')

            # Extract original file if exists
            original_file = self._extract_original_file(content)
            original_content = ""

            if original_file:
                original_path = self.inbox / original_file
                if original_path.exists():
                    original_content = original_path.read_text(encoding='utf-8')

            # Get AI analysis
            analysis = self.ai_client.analyze_task(
                original_content or content,
                context={'task_file': task_path.name}
            )

            # Update task file
            updated_content = content.replace('status: pending', 'status: completed')
            updated_content += f"\n{analysis}\n"

            task_path.write_text(updated_content, encoding='utf-8')
            logger.info(f"Processed task: {task_path.name}")

            return True

        except Exception as e:
            logger.error(f"Error processing task {task_path.name}: {e}")
            return False

    def move_to_done(self, task_path: Path) -> bool:
        """Move completed task to Done folder"""
        try:
            destination = self.done / task_path.name
            shutil.move(str(task_path), str(destination))
            logger.info(f"Moved {task_path.name} to Done")
            return True

        except Exception as e:
            logger.error(f"Error moving task to Done: {e}")
            return False

    def update_dashboard(self, task_name: str):
        """Update Dashboard with completed task"""
        try:
            if not self.dashboard.exists():
                logger.warning("Dashboard.md not found")
                return

            content = self.dashboard.read_text(encoding='utf-8')
            lines = content.split('\n')

            # Find completed tasks section
            for i, line in enumerate(lines):
                if line.strip() == '## Completed Tasks':
                    # Remove "- None" if present
                    if i + 1 < len(lines) and lines[i + 1].strip() == '- None':
                        lines.pop(i + 1)

                    # Add new task
                    today = datetime.now().strftime('%Y-%m-%d')
                    entry = f"- ✅ {task_name} - Processed by AI (Completed: {today})"
                    lines.insert(i + 1, entry)
                    break

            self.dashboard.write_text('\n'.join(lines), encoding='utf-8')
            logger.info(f"Updated dashboard with {task_name}")

        except Exception as e:
            logger.error(f"Error updating dashboard: {e}")

    def _extract_original_file(self, content: str) -> Optional[str]:
        """Extract original file name from task content"""
        for line in content.split('\n'):
            if line.startswith('original_file:'):
                return line.split(':', 1)[1].strip()
        return None
