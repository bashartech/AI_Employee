"""
Orchestrator module - WITH QWEN AI INTEGRATION
Main automation engine that coordinates task processing with Qwen AI (FREE!)
Replaces Claude Code with local Qwen AI via Ollama
"""

import time
import sys
import subprocess
import re
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileCreatedEvent

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    NEEDS_ACTION_FOLDER,
    PENDING_APPROVAL_FOLDER,
    APPROVED_FOLDER,
    DONE_FOLDER,
    REJECTED_FOLDER,
    ensure_folders_exist
)
from engine.approval_manager import ApprovalManager
from engine.logger import logger

# ✨ QWEN AI INTEGRATION - Safe import with fallback ✨
try:
    from engine.qwen_ai import format_email, format_odoo_lead, format_linkedin_post, format_whatsapp_message, check_ollama, check_qwen_model
    QWEN_ENABLED = check_ollama() and check_qwen_model()
    if QWEN_ENABLED:
        print("✅ Qwen AI integration loaded")
    else:
        print("⚠️  Qwen AI not available - using basic templates")
except ImportError:
    QWEN_ENABLED = False
    print("⚠️  Qwen AI module not found - using basic templates")


class TaskHandler(FileSystemEventHandler):
    """Handles file system events for task folders"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
        self.processed_files = set()

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process markdown files
        if file_path.suffix.lower() not in ['.md', '.txt']:
            return

        # Skip if already processed
        if file_path.name in self.processed_files:
            return

        logger.info(f"📥 New file detected: {file_path.name}")

        # Only process Needs Action folder
        if "Needs Action" in str(file_path):
            self.processed_files.add(file_path.name)
            self.orchestrator.process_new_task(file_path)


class Orchestrator:
    """Main orchestrator for AI Employee automation"""
    
    _initialized = False  # ← MUST be at class level, NOT indented!

    def __init__(self):
        """Initialize orchestrator - NO LOGGER AT MODULE LEVEL!"""
        
        # Ensure folders exist
        ensure_folders_exist()

        # Use centralized folder paths
        self.needs_action_folder = NEEDS_ACTION_FOLDER
        self.pending_approval_folder = PENDING_APPROVAL_FOLDER
        self.approved_folder = APPROVED_FOLDER
        self.done_folder = DONE_FOLDER
        self.rejected_folder = REJECTED_FOLDER

        # Initialize components
        self.approval_manager = ApprovalManager(self.pending_approval_folder)

        # File system observer
        self.observer = Observer()

        # Email signature configuration
        self.sender_name = "M. Bashar Sheikh"

        # Track processed files to avoid loops
        self.processed_count = 0

        # ✅ Logger ONLY inside __init__, not at module level!
        logger.info("✅ Orchestrator initialized (with Qwen AI)")

    def start(self):
        """Start the orchestrator"""
        logger.info("🚀 Starting orchestrator...")

        # Process any existing files first
        self._process_existing_files()

        # Set up file watcher for Needs Action folder only
        handler = TaskHandler(self)

        self.observer.schedule(handler, str(self.needs_action_folder), recursive=False)

        self.observer.start()

        logger.info("👀 Orchestrator started. Watching for tasks...")
        logger.info("📌 Note: execute_approved.py handles Approved folder execution")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Stop the orchestrator"""
        logger.info("🛑 Stopping orchestrator...")
        self.observer.stop()
        self.observer.join()
        logger.info("✅ Orchestrator stopped")

    def _process_existing_files(self):
        """Process any files that already exist in Needs Action folder"""
        logger.info("🔍 Checking for existing files...")

        for file_path in self.needs_action_folder.glob("*.md"):
            self.process_new_task(file_path)

        for file_path in self.needs_action_folder.glob("*.txt"):
            self.process_new_task(file_path)

    def process_new_task(self, file_path: Path):
        """Process a new task from Needs Action folder"""
        try:
            logger.info(f"📋 Processing new task: {file_path.name}")

            task_content = file_path.read_text(encoding='utf-8')
            task_type = self._detect_task_type(file_path.name, task_content)

            logger.info(f"🤖 Processing {task_type} task...")
            success = self._process_task_directly(task_type, file_path, task_content)

            if success:
                logger.info(f"✅ Task processed successfully: {file_path.name}")
                self.processed_count += 1
            else:
                logger.warning(f"⚠️ Task processing incomplete: {file_path.name}")

        except Exception as e:
            logger.error(f"❌ Error processing new task {file_path}: {e}")

    def _process_task_directly(self, task_type: str, file_path: Path, task_content: str) -> bool:
        """Process task directly"""
        try:
            if task_type == 'email':
                return self._process_email_task(file_path, task_content)
            elif task_type == 'inbox_email':
                return self._process_inbox_email_task(file_path, task_content)
            elif task_type == 'inbox_whatsapp':
                return self._process_inbox_whatsapp_task(file_path, task_content)
            elif task_type == 'inbox_linkedin':
                return self._process_inbox_linkedin_task(file_path, task_content)
            elif task_type == 'inbox':
                return self._process_generic_inbox_task(file_path, task_content)
            elif task_type == 'whatsapp':
                return self._process_whatsapp_task(file_path, task_content)
            elif task_type == 'linkedin':
                return self._process_linkedin_task(file_path, task_content)
            elif task_type == 'odoo':
                return self._process_odoo_task(file_path, task_content)
            elif task_type == 'general':
                return self._process_generic_inbox_task(file_path, task_content)
            else:
                logger.warning(f"Unknown task type: {task_type}")
                return False
        except Exception as e:
            logger.error(f"Error processing task directly: {e}")
            return False

    def _process_inbox_email_task(self, file_path: Path, task_content: str) -> bool:
        """Process inbox email task - WITH QWEN AI"""
        try:
            import re
            from datetime import datetime

            content_match = re.search(r'## Content\s*\n\n(.+?)(?=\n##|\Z)', task_content, re.DOTALL)

            if not content_match or not content_match.group(1).strip():
                logger.warning("Empty email task content")
                return self._process_generic_inbox_task(file_path, task_content)

            request = content_match.group(1).strip()

            if re.match(r'^File:\s*\w+\s*Type:\s*$', request, re.IGNORECASE):
                logger.warning("No actionable email content")
                return self._process_generic_inbox_task(file_path, task_content)

            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', request)
            if not email_match:
                logger.warning("Could not find recipient email")
                return self._process_generic_inbox_task(file_path, task_content)

            to_email = email_match.group(0)

            # ✨ QWEN AI: Format email with Qwen ✨
            if QWEN_ENABLED:
                try:
                    email_body = format_email(request)
                    subject = "Re: Your Inquiry"
                except Exception as e:
                    logger.warning(f"Qwen failed, using template: {e}")
                    email_body = self._draft_generic_email(request)
                    subject = "Information Request"
            else:
                email_body = self._draft_generic_email(request)
                subject = "Information Request"

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            approval_filename = f"APPROVAL_send_email_{timestamp}.md"
            approval_path = self.pending_approval_folder / approval_filename

            approval_content = f"""---
type: email_approval
action: send_email
to: {to_email}
subject: {subject}
---

# Email Response Approval

## Original Request
{request}

## Email Body
{email_body}

---

## Instructions
1. Review the drafted email above
2. Move to Approved/ to send
3. Move to Rejected/ to cancel
"""

            approval_path.write_text(approval_content, encoding='utf-8')
            logger.info(f"Created approval file: {approval_filename}")

            done_path = self.done_folder / file_path.name
            shutil.move(str(file_path), str(done_path))
            logger.info(f"Moved task to Done: {file_path.name}")

            return True

        except Exception as e:
            logger.error(f"Error processing inbox email task: {e}")
            return False

    def _process_inbox_whatsapp_task(self, file_path: Path, task_content: str) -> bool:
        """Process inbox WhatsApp task - WITH QWEN AI"""
        try:
            import re
            from datetime import datetime

            content_match = re.search(r'## Content\s*\n\n(.+?)(?=\n##|\Z)', task_content, re.DOTALL)

            if not content_match or not content_match.group(1).strip():
                return self._process_generic_inbox_task(file_path, task_content)

            request = content_match.group(1).strip()

            phone_match = re.search(r'\+?\d[\d\s-]{8,}', request)
            if not phone_match:
                return self._process_generic_inbox_task(file_path, task_content)

            phone = phone_match.group(0).replace(' ', '').replace('-', '')

            # ✨ QWEN AI: Format message with Qwen ✨
            if QWEN_ENABLED:
                try:
                    message = format_whatsapp_message(request)
                except Exception as e:
                    logger.warning(f"Qwen failed, using template: {e}")
                    message = f"Hi,\n\nThank you for your message.\n\nBest regards,\n{self.sender_name}"
            else:
                message = f"Hi,\n\nThank you for your message.\n\nBest regards,\n{self.sender_name}"

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            approval_filename = f"APPROVAL_send_whatsapp_{timestamp}.md"
            approval_path = self.pending_approval_folder / approval_filename

            approval_content = f"""---
type: whatsapp_approval
action: send_whatsapp
phone: {phone}
---

# WhatsApp Message Approval

## Original Request
{request}

## Message
{message}

---

## Instructions
1. Review the drafted message above
2. Move to Approved/ to send
"""

            approval_path.write_text(approval_content, encoding='utf-8')
            logger.info(f"Created approval file: {approval_filename}")

            done_path = self.done_folder / file_path.name
            shutil.move(str(file_path), str(done_path))
            logger.info(f"Moved task to Done: {file_path.name}")

            return True

        except Exception as e:
            logger.error(f"Error processing inbox WhatsApp task: {e}")
            return False

    def _process_inbox_linkedin_task(self, file_path: Path, task_content: str) -> bool:
        """Process inbox LinkedIn task - WITH QWEN AI"""
        try:
            import re
            from datetime import datetime

            content_match = re.search(r'## Content\s*\n\n(.+?)(?=\n##|\Z)', task_content, re.DOTALL)

            if not content_match or not content_match.group(1).strip():
                return self._process_generic_inbox_task(file_path, task_content)

            request = content_match.group(1).strip()

            # ✨ QWEN AI: Create post with Qwen ✨
            if QWEN_ENABLED:
                try:
                    post_content = format_linkedin_post(request)
                except Exception as e:
                    logger.warning(f"Qwen failed, using template: {e}")
                    post_content = f"Excited to share some insights!\n\n{request}\n\n#Professional #Business #Growth"
            else:
                post_content = f"Excited to share some insights!\n\n{request}\n\n#Professional #Business #Growth"

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            approval_filename = f"APPROVAL_linkedin_post_{timestamp}.md"
            approval_path = self.pending_approval_folder / approval_filename

            approval_content = f"""---
type: linkedin_approval
action: linkedin_post
---

# LinkedIn Post Approval

## Original Request
{request}

## Post Content
{post_content}

---

## Instructions
1. Review the drafted post above
2. Move to Approved/ to publish
"""

            approval_path.write_text(approval_content, encoding='utf-8')
            logger.info(f"Created approval file: {approval_filename}")

            done_path = self.done_folder / file_path.name
            shutil.move(str(file_path), str(done_path))
            logger.info(f"Moved task to Done: {file_path.name}")

            return True

        except Exception as e:
            logger.error(f"Error processing inbox LinkedIn task: {e}")
            return False

    def _process_generic_inbox_task(self, file_path: Path, task_content: str) -> bool:
        """Process generic inbox task"""
        try:
            import re
            from datetime import datetime

            content_match = re.search(r'## Content\s*\n\n(.+?)(?=\n##|\Z)', task_content, re.DOTALL)
            request = content_match.group(1).strip() if content_match else "No content"

            filename_lower = file_path.name.lower()
            request_lower = request.lower()

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

            is_linkedin = ('linkedin' in filename_lower or 'linkedin' in request_lower or 'post' in request_lower)
            is_email = ('email' in filename_lower or 'email' in request_lower)
            is_whatsapp = ('whatsapp' in filename_lower or 'whatsapp' in request_lower)

            if is_linkedin:
                approval_filename = f"APPROVAL_linkedin_post_{timestamp}.md"
                approval_path = self.pending_approval_folder / approval_filename
                approval_content = f"""---
type: linkedin_approval
action: linkedin_post
---

# LinkedIn Post Approval

## Content
{request}

---
## Instructions
Move to Approved/ to publish
"""
            elif is_email:
                email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', request)
                to_email = email_match.group(0) if email_match else "recipient@example.com"
                
                approval_filename = f"APPROVAL_send_email_{timestamp}.md"
                approval_path = self.pending_approval_folder / approval_filename
                approval_content = f"""---
type: email_approval
action: send_email
to: {to_email}
subject: Re: Inquiry
---

# Email Response Approval

## Content
{request}

---
## Instructions
Move to Approved/ to send
"""
            else:
                approval_filename = f"NOTE_manual_review_{timestamp}.md"
                approval_path = self.pending_approval_folder / approval_filename
                approval_content = f"""---
type: manual_review
action: review_required
---

# Manual Review Required

## Content
{request}

---
## Instructions
Manual review needed
"""

            approval_path.write_text(approval_content, encoding='utf-8')
            logger.info(f"Created approval file: {approval_filename}")

            done_path = self.done_folder / file_path.name
            shutil.move(str(file_path), str(done_path))
            logger.info(f"Moved task to Done: {file_path.name}")

            return True

        except Exception as e:
            logger.error(f"Error processing generic inbox task: {e}")
            return False

    def _process_odoo_task(self, file_path: Path, task_content: str) -> bool:
        """Process Odoo task - WITH QWEN AI"""
        try:
            import re
            from datetime import datetime

            content_match = re.search(r'## Content\s*\n\n(.+?)(?=\n##|\Z)', task_content, re.DOTALL)
            request = content_match.group(1).strip() if content_match else ""

            # ✨ QWEN AI: Extract lead info with Qwen ✨
            if QWEN_ENABLED:
                try:
                    formatted = format_odoo_lead(request)
                    from engine.qwen_ai import parse_lead_info
                    lead_info = parse_lead_info(formatted)
                    lead_name = lead_info['name']
                    email = lead_info['email']
                    phone = lead_info['phone']
                    source = lead_info['source']
                except Exception as e:
                    logger.warning(f"Qwen failed, using basic extraction: {e}")
                    lead_name, email, phone, source = self._extract_lead_basic(request)
            else:
                lead_name, email, phone, source = self._extract_lead_basic(request)

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            approval_filename = f"ODOO_LEAD_{lead_name.replace(' ', '_')}_{timestamp}.md"
            approval_path = self.pending_approval_folder / approval_filename

            approval_content = f"""---
type: odoo_approval
action: create_lead
lead_name: {lead_name}
email: {email}
phone: {phone}
source: {source}
---

# Odoo Lead Creation Approval

## Lead Information
**Name:** {lead_name}
**Email:** {email}
**Phone:** {phone}
**Source:** {source}

## Instructions
1. Review the lead information above
2. Move to Approved/ to create in Odoo
"""

            approval_path.write_text(approval_content, encoding='utf-8')
            logger.info(f"Created Odoo approval file: {approval_filename}")

            done_path = self.done_folder / file_path.name
            shutil.move(str(file_path), str(done_path))
            logger.info(f"Moved {file_path.name} to Done/")

            return True

        except Exception as e:
            logger.error(f"Error processing Odoo task: {e}")
            return False

    def _extract_lead_basic(self, request: str) -> tuple:
        """Basic lead extraction without AI"""
        import re
        
        name_match = re.search(r'name:\s*(.+?)(?:\n|$)', request, re.IGNORECASE)
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', request)
        phone_match = re.search(r'phone:\s*(\+?[\d\s-]{8,})', request, re.IGNORECASE)
        source_match = re.search(r'source:\s*(.+?)(?:\n|$)', request, re.IGNORECASE)
        
        lead_name = name_match.group(1).strip() if name_match else "Unknown Lead"
        email = email_match.group(0) if email_match else ""
        phone = phone_match.group(1).strip() if phone_match else ""
        source = source_match.group(1).strip() if source_match else "Dashboard"
        
        return lead_name, email, phone, source

    def _draft_generic_email(self, request: str) -> str:
        """Draft generic email without AI"""
        return f"""Dear Valued Client,

Thank you for reaching out to us.

{request}

We appreciate your business and look forward to serving you better.

Best regards,
{self.sender_name}"""

    def _process_email_task(self, file_path: Path, task_content: str) -> bool:
        """Process email task"""
        return self._process_inbox_email_task(file_path, task_content)

    def _process_whatsapp_task(self, file_path: Path, task_content: str) -> bool:
        """Process WhatsApp task"""
        return self._process_inbox_whatsapp_task(file_path, task_content)

    def _process_linkedin_task(self, file_path: Path, task_content: str) -> bool:
        """Process LinkedIn task"""
        return self._process_inbox_linkedin_task(file_path, task_content)

    def _detect_task_type(self, filename: str, content: str) -> str:
        """Detect task type"""
        filename_lower = filename.lower()
        content_lower = content.lower()

        # Odoo detection
        odoo_keywords = ['odoo', 'oddo', 'odo', 'lead', 'crm', 'invoice', 'quotation']
        if any(keyword in content_lower for keyword in odoo_keywords) or 'odoo' in filename_lower:
            return 'odoo'

        if 'send email' in content_lower or 'send whatsapp' in content_lower:
            return 'inbox_email'

        # Inbox detection
        if 'inbox' in filename_lower or 'source:** inbox' in content_lower:
            if 'email' in content_lower or 'email' in filename_lower:
                return 'inbox_email'
            elif 'whatsapp' in content_lower or 'whatsapp' in filename_lower:
                return 'inbox_whatsapp'
            elif 'linkedin' in content_lower or 'linkedin' in filename_lower:
                return 'inbox_linkedin'

            import re
            if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content):
                return 'inbox_email'

            if re.search(r'\+?\d[\d\s-]{8,}', content):
                return 'inbox_whatsapp'

            if any(word in content_lower for word in ['post', 'linkedin', 'social media']):
                return 'inbox_linkedin'

            return 'inbox'

        if 'email' in filename_lower or 'type: email' in content_lower:
            return 'email'
        elif 'whatsapp' in filename_lower or 'type: whatsapp' in content_lower:
            return 'whatsapp'
        elif 'linkedin' in filename_lower or 'type: linkedin' in content_lower:
            return 'linkedin'
        else:
            return 'general'

    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            'needs_action': len(list(self.needs_action_folder.glob("*.md"))),
            'pending_approval': len(list(self.pending_approval_folder.glob("*.md"))),
            'approved': len(list(self.approved_folder.glob("*.md"))),
            'done': len(list(self.done_folder.glob("*.md"))),
            'rejected': len(list(self.rejected_folder.glob("*.md"))),
            'processed_count': self.processed_count
        }

if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.start()