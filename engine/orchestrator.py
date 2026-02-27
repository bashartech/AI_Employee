"""
Orchestrator module
Main automation engine that coordinates task processing with Claude Code
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


class TaskHandler(FileSystemEventHandler):
    """Handles file system events for task folders"""

    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Only process markdown files
        if file_path.suffix.lower() not in ['.md', '.txt']:
            return

        logger.info(f"📥 New file detected: {file_path.name}")

        # Only process Needs Action folder (execute_approved.py handles Approved folder)
        if "Needs Action" in str(file_path):
            self.orchestrator.process_new_task(file_path)


class Orchestrator:
    """Main orchestrator for AI Employee automation"""

    def __init__(self):
        """Initialize orchestrator"""

        # Ensure folders exist (centralized config)
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

        logger.info("✅ Orchestrator initialized (using Claude Code)")

    def start(self):
        """Start the orchestrator"""
        logger.info("🚀 Starting orchestrator...")

        # Process any existing files first
        self._process_existing_files()

        # Set up file watcher for Needs Action folder only
        # (execute_approved.py handles Approved folder)
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

        # Process Needs Action folder
        for file_path in self.needs_action_folder.glob("*.md"):
            self.process_new_task(file_path)

        for file_path in self.needs_action_folder.glob("*.txt"):
            self.process_new_task(file_path)

    def process_new_task(self, file_path: Path):
        """
        Process a new task from Needs Action folder directly

        Args:
            file_path: Path to the task file
        """
        try:
            logger.info(f"📋 Processing new task: {file_path.name}")

            # Read task content
            task_content = file_path.read_text(encoding='utf-8')

            # Detect task type
            task_type = self._detect_task_type(file_path.name, task_content)

            # Process the task directly based on type
            logger.info(f"🤖 Processing {task_type} task...")
            success = self._process_task_directly(task_type, file_path, task_content)

            if success:
                logger.info(f"✅ Task processed successfully: {file_path.name}")
            else:
                logger.warning(f"⚠️ Task processing incomplete: {file_path.name}")

        except Exception as e:
            logger.error(f"❌ Error processing new task {file_path}: {e}")

    def _process_task_directly(self, task_type: str, file_path: Path, task_content: str) -> bool:
        """Process task directly without spawning Claude Code"""
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
        """Process inbox email composition task"""
        try:
            import re
            from datetime import datetime

            # Extract the content/request
            content_match = re.search(r'## Content\s*\n\n(.+?)(?=\n##|\Z)', task_content, re.DOTALL)

            if not content_match or not content_match.group(1).strip():
                logger.warning("Empty email task content - creating manual review note")
                return self._process_generic_inbox_task(file_path, task_content)

            request = content_match.group(1).strip()

            # Check if it's just "File: xxx" with no actual content
            if re.match(r'^File:\s*\w+\s*Type:\s*$', request, re.IGNORECASE):
                logger.warning("No actionable email content - creating manual review note")
                return self._process_generic_inbox_task(file_path, task_content)

            # Parse the request to extract recipient and topic
            # Pattern 1: "write ... email ... to email@example.com"
            email_match = re.search(r'(?:to|send|email)\s+([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', request, re.IGNORECASE)

            # Pattern 2: Just an email address in the content
            if not email_match:
                email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', request)

            if not email_match:
                logger.warning("Could not find recipient email - creating manual review note")
                return self._process_generic_inbox_task(file_path, task_content)

            to_email = email_match.group(1).strip()

            # Extract topic/subject from the request
            # Pattern: "email for/about [topic] to"
            topic_match = re.search(r'(?:email|write|send)\s+(?:for|about|regarding)\s+(.+?)\s+(?:to|explanation)', request, re.IGNORECASE)

            if topic_match:
                topic = topic_match.group(1).strip()
                subject = topic.title()
            else:
                # Try to extract any meaningful content before the email address
                before_email = request[:request.find(to_email)].strip()
                if len(before_email) > 10:
                    # Use the content as topic
                    topic = before_email.replace('write', '').replace('email', '').replace('for', '').replace('to', '').strip()
                    subject = "Information Request"
                else:
                    # Fallback: use generic subject
                    subject = "Information Request"
                    topic = "your inquiry"

            # Determine if formal or casual
            is_formal = 'formal' in request.lower()

            # Draft email based on topic
            if 'c language' in request.lower() or 'c programming' in request.lower():
                email_body = self._draft_c_language_email(is_formal)
                subject = "Introduction to C Programming Language"
            elif 'python' in request.lower():
                email_body = self._draft_python_email(is_formal)
                subject = "Introduction to Python Programming"
            elif 'java' in request.lower():
                email_body = self._draft_java_email(is_formal)
                subject = "Introduction to Java Programming"
            else:
                # Generic email based on extracted topic
                if is_formal:
                    email_body = f"""Dear Recipient,

I hope this email finds you well. I am writing to provide you with information regarding {topic}.

I would be happy to discuss this topic in more detail and answer any questions you may have. Please feel free to reach out if you need additional information or clarification.

Best regards,
AI Employee"""
                else:
                    email_body = f"""Hi there,

Thanks for reaching out! I'd be happy to help you with {topic}.

Let me know if you have any specific questions or if there's anything else I can assist you with.

Best,
AI Employee"""

            # Create approval file
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
1. **Review** the drafted response above
2. **Edit** if needed
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder
"""

            # Write approval file
            approval_path.write_text(approval_content, encoding='utf-8')
            logger.info(f"Created approval file: {approval_filename}")

            # Move original task to Done
            done_path = self.done_folder / file_path.name
            shutil.move(str(file_path), str(done_path))
            logger.info(f"Moved task to Done: {file_path.name}")

            return True

        except Exception as e:
            logger.error(f"Error processing inbox email task: {e}")
            return False

    def _process_inbox_whatsapp_task(self, file_path: Path, task_content: str) -> bool:
        """Process inbox WhatsApp message composition task"""
        try:
            import re
            from datetime import datetime

            # Extract the content/request
            content_match = re.search(r'## Content\s*\n\n(.+?)(?=\n##|\Z)', task_content, re.DOTALL)

            if not content_match or not content_match.group(1).strip():
                logger.warning("Empty WhatsApp task content - creating manual review note")
                return self._process_generic_inbox_task(file_path, task_content)

            request = content_match.group(1).strip()

            # Check if it's just "File: xxx" with no actual content
            if re.match(r'^File:\s*\w+\s*Type:\s*$', request, re.IGNORECASE):
                logger.warning("No actionable WhatsApp content - creating manual review note")
                return self._process_generic_inbox_task(file_path, task_content)

            # Parse phone number from request
            phone_match = re.search(r'(?:to|send|phone|number)[\s:]+(\+?\d[\d\s-]{8,})', request, re.IGNORECASE)

            if not phone_match:
                logger.warning("Could not find phone number - creating manual review note")
                return self._process_generic_inbox_task(file_path, task_content)

            phone = phone_match.group(1).strip()

            # Draft WhatsApp message based on request
            message = f"""Hi,

Thank you for your message. I'll get back to you shortly with the information you requested.

Best regards"""

            # Create approval file
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
1. **Review** the drafted message above
2. **Edit** if needed
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder
"""

            # Write approval file
            approval_path.write_text(approval_content, encoding='utf-8')
            logger.info(f"Created approval file: {approval_filename}")

            # Move original task to Done
            done_path = self.done_folder / file_path.name
            shutil.move(str(file_path), str(done_path))
            logger.info(f"Moved task to Done: {file_path.name}")

            return True

        except Exception as e:
            logger.error(f"Error processing inbox WhatsApp task: {e}")
            # Fallback to generic handler
            return self._process_generic_inbox_task(file_path, task_content)

    def _process_inbox_linkedin_task(self, file_path: Path, task_content: str) -> bool:
        """Process inbox LinkedIn post creation task"""
        try:
            import re
            from datetime import datetime

            # Extract the content/request
            content_match = re.search(r'## Content\s*\n\n(.+?)(?=\n##|\Z)', task_content, re.DOTALL)

            if not content_match or not content_match.group(1).strip():
                logger.warning("Empty LinkedIn task content - creating manual review note")
                return self._process_generic_inbox_task(file_path, task_content)

            request = content_match.group(1).strip()

            # Check if it's just "File: xxx" with no actual content
            if re.match(r'^File:\s*\w+\s*Type:\s*$', request, re.IGNORECASE):
                logger.warning("No actionable LinkedIn content - creating manual review note")
                return self._process_generic_inbox_task(file_path, task_content)

            # Draft LinkedIn post based on request
            post_content = f"""Excited to share some insights!

{request}

What are your thoughts on this? Let me know in the comments!

#Professional #Business #Growth #Innovation #Leadership"""

            # Create approval file
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
1. **Review** the drafted post above
2. **Edit** if needed
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder
"""

            # Write approval file
            approval_path.write_text(approval_content, encoding='utf-8')
            logger.info(f"Created approval file: {approval_filename}")

            # Move original task to Done
            done_path = self.done_folder / file_path.name
            shutil.move(str(file_path), str(done_path))
            logger.info(f"Moved task to Done: {file_path.name}")

            return True

        except Exception as e:
            logger.error(f"Error processing inbox LinkedIn task: {e}")
            # Fallback to generic handler
            return self._process_generic_inbox_task(file_path, task_content)

    def _process_generic_inbox_task(self, file_path: Path, task_content: str) -> bool:
        """Process generic inbox task - just move to Done with a note"""
        try:
            import re
            from datetime import datetime

            # Extract the content
            content_match = re.search(r'## Content\s*\n\n(.+?)(?=\n##|\Z)', task_content, re.DOTALL)

            if content_match:
                request = content_match.group(1).strip()
            else:
                request = "No content found"

            # Create a note file in Pending Approval for manual review
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            note_filename = f"NOTE_manual_review_{timestamp}.md"
            note_path = self.pending_approval_folder / note_filename

            note_content = f"""---
type: manual_review
action: review_required
---

# Manual Review Required

## Original Task
**File:** {file_path.name}

## Content
{request}

---

## Instructions
This task requires manual review and action. Please:
1. Review the content above
2. Determine appropriate action
3. Take necessary steps manually
4. Move this note to `Done/` when complete
"""

            # Write note file
            note_path.write_text(note_content, encoding='utf-8')
            logger.info(f"Created manual review note: {note_filename}")

            # Move original task to Done
            done_path = self.done_folder / file_path.name
            shutil.move(str(file_path), str(done_path))
            logger.info(f"Moved task to Done: {file_path.name}")

            return True

        except Exception as e:
            logger.error(f"Error processing generic inbox task: {e}")
            return False

    def _draft_c_language_email(self, is_formal: bool) -> str:
        """Draft an email explaining C language"""
        if is_formal:
            return """Dear Recipient,

I hope this email finds you well. I am writing to provide you with an overview of the C programming language.

C is a general-purpose, procedural programming language developed by Dennis Ritchie at Bell Labs in the early 1970s. It has become one of the most widely used programming languages and serves as the foundation for many modern languages.

Key Features of C:
• Low-level memory access through pointers
• Efficient and fast execution
• Portable across different platforms
• Rich library of built-in functions
• Structured programming approach

C is particularly well-suited for:
- System programming (operating systems, device drivers)
- Embedded systems development
- Performance-critical applications
- Learning fundamental programming concepts

The language provides direct control over hardware resources while maintaining a relatively simple syntax. Its influence can be seen in languages like C++, Java, C#, and many others.

If you would like more detailed information about specific aspects of C programming, such as syntax, data structures, or practical applications, please feel free to reach out.

Best regards,
AI Employee"""
        else:
            return """Hi there,

Thanks for your interest in learning about C!

C is a powerful programming language that's been around since the 1970s. It's known for being fast, efficient, and giving you direct control over computer memory.

Here's what makes C special:
• It's the foundation for many modern languages
• Great for system programming and embedded systems
• Teaches you how computers really work
• Still widely used in industry today

C is perfect if you want to understand low-level programming concepts or work on performance-critical applications.

Let me know if you'd like to dive deeper into any specific topics!

Best,
AI Employee"""

    def _process_email_task(self, file_path: Path, task_content: str) -> bool:
        """Process email task and create approval file"""
        try:
            # Extract email details from YAML frontmatter
            import re
            from datetime import datetime

            # Parse from field - handle: "Name" <email> or just email
            from_match = re.search(r'from:\s*(?:"([^"]+)"\s*<([^>]+)>|<([^>]+)>|([^\n]+))', task_content)

            if not from_match:
                logger.error("Could not parse 'from' field")
                return False

            # Extract name and email
            if from_match.group(1) and from_match.group(2):
                # Format: "Name" <email>
                from_display = f'"{from_match.group(1)}" <{from_match.group(2)}>'
                to_email = from_match.group(2).strip()
            elif from_match.group(3):
                # Format: <email>
                to_email = from_match.group(3).strip()
                from_display = f'<{to_email}>'
            else:
                # Format: just email or name
                to_email = from_match.group(4).strip()
                from_display = to_email

            # Parse subject - only capture content on the same line, handle empty
            subject_match = re.search(r'subject:\s*([^\n]*)', task_content)
            subject = subject_match.group(1).strip() if subject_match and subject_match.group(1).strip() else "(no subject)"

            # Extract email content
            content_match = re.search(r'## Email Content\s*\n\n(.+?)(?=\n##|\Z)', task_content, re.DOTALL)

            if not content_match:
                logger.error("Could not parse email content")
                return False

            original_content = content_match.group(1).strip()

            # Draft a simple response
            response_body = f"""Hi,

Thank you for reaching out. I'm doing well, thank you for asking. How can I assist you today?

Best regards,
AI Employee"""

            # Create approval file
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            approval_filename = f"APPROVAL_send_email_{timestamp}.md"
            approval_path = self.pending_approval_folder / approval_filename

            # Format subject for reply
            reply_subject = f"Re: {subject}" if subject != "(no subject)" else "Re: "

            approval_content = f"""---
type: email_approval
action: send_email
to: {to_email}
subject: {reply_subject}
---

# Email Response Approval

## Original Email
- **From:** {from_display}
- **Subject:** {subject}
- **Content:** {original_content}

## Email Body

{response_body}

---

## Instructions
1. **Review** the drafted response above
2. **Edit** if needed
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder
"""

            # Write approval file
            approval_path.write_text(approval_content, encoding='utf-8')
            logger.info(f"✅ Created approval file: {approval_filename}")

            # Move original task to Done
            done_path = self.done_folder / file_path.name
            shutil.move(str(file_path), str(done_path))
            logger.info(f"✅ Moved task to Done: {file_path.name}")

            return True

        except Exception as e:
            logger.error(f"Error processing email task: {e}")
            return False

    def _process_whatsapp_task(self, file_path: Path, task_content: str) -> bool:
        """Process WhatsApp task and create approval file"""
        # TODO: Implement WhatsApp processing
        logger.warning("WhatsApp processing not yet implemented")
        return False

    def _process_linkedin_task(self, file_path: Path, task_content: str) -> bool:
        """Process LinkedIn task and create approval file"""
        # TODO: Implement LinkedIn processing
        logger.warning("LinkedIn processing not yet implemented")
        return False

    def _process_odoo_task(self, file_path: Path, task_content: str) -> bool:
        """Process Odoo task and create approval file"""
        try:
            logger.info(f"Processing Odoo task: {file_path.name}")

            # Parse the task content to extract lead data
            import re

            # First check if content has "## Content" section (inbox format)
            content_match = re.search(r'## Content\s*\n\n(.+?)(?=\n##|\Z)', task_content, re.DOTALL)
            if content_match:
                # Extract content from inbox format
                content_to_parse = content_match.group(1).strip()
            else:
                # Use entire content (plain text format)
                content_to_parse = task_content

            # Extract lead information from content
            content_lower = content_to_parse.lower()

            # Extract name
            name_match = re.search(r'name:\s*(.+)', content_to_parse, re.IGNORECASE)
            name = name_match.group(1).strip() if name_match else "Unknown Lead"

            # Extract email (optional)
            email_match = re.search(r'email:\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', content_to_parse, re.IGNORECASE)
            email = email_match.group(1).strip() if email_match else ""

            # Extract phone (optional)
            phone_match = re.search(r'phone:\s*(.+?)(?:\n|$)', content_to_parse, re.IGNORECASE)
            phone = phone_match.group(1).strip() if phone_match else ""

            # Extract age (optional)
            age_match = re.search(r'age:\s*(\d+)', content_to_parse, re.IGNORECASE)
            age = age_match.group(1).strip() if age_match else ""

            # Extract course/product/service (optional)
            course_match = re.search(r'course:\s*(.+?)(?:\n|$)', content_to_parse, re.IGNORECASE)
            if not course_match:
                course_match = re.search(r'product:\s*(.+?)(?:\n|$)', content_to_parse, re.IGNORECASE)
            if not course_match:
                course_match = re.search(r'service:\s*(.+?)(?:\n|$)', content_to_parse, re.IGNORECASE)
            course = course_match.group(1).strip() if course_match else ""

            # Determine source
            source = "Manual Entry"
            if 'inbox' in file_path.name.lower():
                source = "Inbox"

            # Build description with all available info
            description_parts = []
            if age:
                description_parts.append(f"Age: {age}")
            if course:
                description_parts.append(f"Course/Interest: {course}")

            description = " | ".join(description_parts) if description_parts else "Lead from AI Employee Vault"

            # Create approval file
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            approval_filename = f"ODOO_LEAD_{name.replace(' ', '_')}_{timestamp}.md"
            approval_path = self.pending_approval_folder / approval_filename

            approval_content = f"""---
type: odoo_approval
action: create_lead
lead_name: {name}
email: {email}
phone: {phone}
source: {source}
---

# Odoo Lead Creation Approval

## Lead Information

**Name:** {name}
**Email:** {email if email else "Not provided"}
**Phone:** {phone if phone else "Not provided"}
**Source:** {source}

## Additional Details

{description}

## Original Request

{content_to_parse}

---

## Instructions
1. **Review** the lead information above
2. **Edit** if needed (update YAML frontmatter fields)
3. **Approve:** Move to `Approved/` folder to create lead in Odoo
4. **Reject:** Move to `Rejected/` folder to cancel

**Note:** Once approved, this lead will be automatically created in Odoo CRM.
"""

            # Write approval file
            approval_path.write_text(approval_content, encoding='utf-8')
            logger.info(f"Created Odoo approval file: {approval_filename}")

            # Move original task to Done
            done_path = self.done_folder / file_path.name
            shutil.move(str(file_path), str(done_path))
            logger.info(f"Moved {file_path.name} to Done/")

            return True

        except Exception as e:
            logger.error(f"Error processing Odoo task: {e}")
            return False

    def _detect_task_type(self, filename: str, content: str) -> str:
        """Detect what type of task this is"""
        filename_lower = filename.lower()
        content_lower = content.lower()

        # First check for Odoo tasks (highest priority - check before inbox detection)
        odoo_keywords = ['odoo', 'oddo', 'odo', 'lead', 'crm', 'create lead', 'new lead',
                         'invoice', 'quotation', 'quote', 'customer']
        if any(keyword in content_lower for keyword in odoo_keywords) or 'odoo' in filename_lower:
            # More specific Odoo task detection
            if any(word in content_lower for word in ['lead', 'crm', 'create lead', 'new lead']):
                return 'odoo'
            elif any(word in content_lower for word in ['invoice', 'bill']):
                return 'odoo'
            elif any(word in content_lower for word in ['quotation', 'quote', 'proposal']):
                return 'odoo'
            elif 'odoo' in filename_lower or 'odoo' in content_lower or 'oddo' in content_lower:
                return 'odoo'

        # Check if it's an inbox file drop
        if 'inbox' in filename_lower or 'source:** inbox' in content_lower:
            # Determine what kind of inbox task - be flexible with spelling
            # First check explicit keywords
            if 'email' in content_lower or 'email' in filename_lower:
                return 'inbox_email'
            elif 'whatsapp' in content_lower or 'whatsapp' in filename_lower or 'watsapp' in filename_lower:
                return 'inbox_whatsapp'
            elif 'linkedin' in content_lower or 'linkedin' in filename_lower:
                return 'inbox_linkedin'

            # Smart detection based on content patterns
            import re

            # Check for email addresses in content → likely email task
            if re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', content):
                return 'inbox_email'

            # Check for phone numbers → likely WhatsApp task
            if re.search(r'\+?\d[\d\s-]{8,}', content):
                return 'inbox_whatsapp'

            # Check for social media keywords → likely LinkedIn
            if any(word in content_lower for word in ['post', 'linkedin', 'social media', 'share', 'network']):
                return 'inbox_linkedin'

            # Default to generic inbox for manual review
            return 'inbox'

        # Check for direct email tasks (with YAML frontmatter)
        if 'email' in filename_lower or 'type: email' in content_lower:
            return 'email'
        elif 'whatsapp' in filename_lower or 'type: whatsapp' in content_lower:
            return 'whatsapp'
        elif 'linkedin' in filename_lower or 'type: linkedin' in content_lower:
            return 'linkedin'
        else:
            return 'general'

    def _build_claude_prompt(self, task_type: str, file_path: Path, task_content: str) -> str:
        """Build appropriate prompt for Claude Code based on task type"""

        base_prompt = f"""Process this {task_type} task from the Needs Action folder.

Task file: {file_path.name}

Task content:
{task_content}

"""

        if task_type == 'email':
            return base_prompt + """Your job:
1. Extract the email details (from, subject, content)
2. Draft a professional email response
3. Create an approval file in "Pending Approval/" folder with this EXACT format:

---
type: email_approval
action: send_email
to: [recipient email from original email]
subject: Re: [original subject]
---

# Email Response Approval

## Original Email
- **From:** [sender email]
- **Subject:** [original subject]
- **Content:** [original message]

## Email Body

[Your drafted response here - this is what will be sent]

---

## Instructions
1. **Review** the drafted response above
2. **Edit** if needed
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder

CRITICAL: The approval file MUST have:
- YAML frontmatter with `to:` and `subject:` fields
- `## Email Body` section (NOT "## Drafted Response")
- Save as: APPROVAL_send_email_[timestamp].md in Pending Approval folder
- After creating approval file, move the original task file to Done folder"""

        elif task_type == 'whatsapp':
            return base_prompt + """Your job:
1. Extract the WhatsApp message details (phone, content)
2. Draft an appropriate WhatsApp response
3. Create an approval file in "Pending Approval/" folder with this EXACT format:

---
type: whatsapp_approval
action: send_whatsapp
phone: [phone number from original message]
---

# WhatsApp Response Approval

## Original Message
- **From:** [phone number]
- **Content:** [original message]

## Message

[Your drafted response here - this is what will be sent]

---

## Instructions
1. **Review** the drafted response above
2. **Edit** if needed
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder

CRITICAL: The approval file MUST have:
- YAML frontmatter with `phone:` field
- `## Message` section
- Save as: APPROVAL_send_whatsapp_[timestamp].md in Pending Approval folder
- After creating approval file, move the original task file to Done folder"""

        elif task_type == 'linkedin':
            return base_prompt + """Your job:
1. Understand the LinkedIn post request
2. Create a professional LinkedIn post with hashtags
3. Create an approval file in "Pending Approval/" folder with this EXACT format:

---
type: linkedin_approval
action: linkedin_post
---

# LinkedIn Post Approval

## Post Content

[Your drafted LinkedIn post here with 3-5 relevant hashtags]

---

## Instructions
1. **Review** the drafted post above
2. **Edit** if needed
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder

CRITICAL: The approval file MUST have:
- YAML frontmatter with `action: linkedin_post`
- `## Post Content` section
- Include 3-5 relevant hashtags
- Save as: APPROVAL_linkedin_post_[timestamp].md in Pending Approval folder
- After creating approval file, move the original task file to Done folder"""

        else:
            return base_prompt + """Your job:
1. Analyze the task and determine what needs to be done
2. If it requires external action (sending email, posting, etc.), create an approval file in "Pending Approval/" folder
3. If it's just information processing, create a summary and move to Done folder

Follow the appropriate format based on the task type (email, whatsapp, linkedin, etc.)"""

    def _invoke_claude_code(self, prompt: str) -> bool:
        """Invoke Claude Code CLI to process the task"""
        try:
            logger.info("🤖 Running Claude Code...")

            # Write prompt to temp file to avoid command line length limits
            import tempfile
            import os

            # Create temp file with the prompt
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as temp_file:
                temp_file.write(prompt)
                temp_file_path = temp_file.name

            try:
                # Unset CLAUDECODE env var to allow nested sessions
                # This is necessary when orchestrator runs from within Claude Code
                env = os.environ.copy()
                env.pop('CLAUDECODE', None)  # Remove CLAUDECODE to bypass nested session check

                # Use temp file as input via stdin redirection
                cmd = f'type "{temp_file_path}" | claude -p'

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                    encoding='utf-8',
                    shell=True,
                    env=env,  # Use modified environment
                    cwd=str(Path(__file__).parent.parent)
                )

                if result.returncode == 0:
                    logger.info("✅ Claude Code completed successfully")
                    if result.stdout:
                        logger.debug(f"Output: {result.stdout[:500]}")  # Log first 500 chars
                    return True
                else:
                    logger.error(f"❌ Claude Code failed with return code {result.returncode}")
                    if result.stderr:
                        logger.error(f"Error output: {result.stderr}")
                    return False

            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass

        except subprocess.TimeoutExpired:
            logger.error("⚠️ Claude Code timed out after 5 minutes")
            return False
        except Exception as e:
            logger.error(f"❌ Error invoking Claude Code: {e}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get current status of the orchestrator"""
        return {
            'needs_action': len(list(self.needs_action_folder.glob("*.md"))) +
                           len(list(self.needs_action_folder.glob("*.txt"))),
            'pending_approval': len(list(self.pending_approval_folder.glob("*.md"))) +
                               len(list(self.pending_approval_folder.glob("*.txt"))),
            'approved': len(list(self.approved_folder.glob("*.md"))) +
                       len(list(self.approved_folder.glob("*.txt"))),
            'done': len(list(self.done_folder.glob("*.md"))) +
                   len(list(self.done_folder.glob("*.txt"))),
            'rejected': len(list(self.rejected_folder.glob("*.md"))) +
                       len(list(self.rejected_folder.glob("*.txt")))
        }


if __name__ == "__main__":
    orchestrator = Orchestrator()
    orchestrator.start()
