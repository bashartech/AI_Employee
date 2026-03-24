"""
Orchestrator module - TEMPLATE-BASED (No AI)
Main automation engine with professional templates for all task types
"""

import time
import sys
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

    def __init__(self):
        """Initialize orchestrator"""
        ensure_folders_exist()

        self.needs_action_folder = NEEDS_ACTION_FOLDER
        self.pending_approval_folder = PENDING_APPROVAL_FOLDER
        self.approved_folder = APPROVED_FOLDER
        self.done_folder = DONE_FOLDER
        self.rejected_folder = REJECTED_FOLDER

        self.approval_manager = ApprovalManager(self.pending_approval_folder)
        self.observer = Observer()
        self.sender_name = "M. Bashar Sheikh"
        self.processed_count = 0

        logger.info("✅ Orchestrator initialized (TEMPLATE MODE)")

    def start(self):
        """Start the orchestrator"""
        logger.info("🚀 Starting orchestrator...")
        self._process_existing_files()

        handler = TaskHandler(self)
        self.observer.schedule(handler, str(self.needs_action_folder), recursive=False)
        self.observer.start()

        logger.info("👀 Orchestrator started. Watching for tasks...")

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
        """Process existing files"""
        logger.info("🔍 Checking for existing files...")
        for file_path in self.needs_action_folder.glob("*.md"):
            self.process_new_task(file_path)
        for file_path in self.needs_action_folder.glob("*.txt"):
            self.process_new_task(file_path)

    def process_new_task(self, file_path: Path):
        """Process new task"""
        try:
            logger.info(f"📋 Processing: {file_path.name}")
            task_content = file_path.read_text(encoding='utf-8')
            task_type = self._detect_task_type(file_path.name, task_content)
            logger.info(f"🤖 Processing {task_type} task...")
            success = self._process_task_directly(task_type, file_path, task_content)

            if success:
                logger.info(f"✅ Task processed: {file_path.name}")
                self.processed_count += 1
            else:
                logger.warning(f"⚠️ Task incomplete: {file_path.name}")
        except Exception as e:
            logger.error(f"❌ Error: {e}")

    def _process_task_directly(self, task_type: str, file_path: Path, task_content: str) -> bool:
        """Process task based on type"""
        try:
            if task_type == 'email' or task_type == 'inbox_email':
                return self._process_email_task(file_path, task_content)
            elif task_type == 'inbox_whatsapp':
                return self._process_whatsapp_task(file_path, task_content)
            elif task_type == 'inbox_linkedin':
                return self._process_linkedin_task(file_path, task_content)
            elif task_type == 'odoo':
                return self._process_odoo_task(file_path, task_content)
            elif task_type == 'inbox':
                return self._process_generic_task(file_path, task_content)
            elif task_type == 'whatsapp':
                return self._process_whatsapp_task(file_path, task_content)
            elif task_type == 'linkedin':
                return self._process_linkedin_task(file_path, task_content)
            elif task_type == 'general':
                return self._process_generic_task(file_path, task_content)
            else:
                logger.warning(f"Unknown type: {task_type}")
                return False
        except Exception as e:
            logger.error(f"Error: {e}")
            return False

    def _process_email_task(self, file_path: Path, task_content: str) -> bool:
        """Process email with PROFESSIONAL template"""
        try:
            import re
            from datetime import datetime

            content_match = re.search(r'## Content\s*\n\n(.+?)(?=\n##|\Z)', task_content, re.DOTALL)
            if not content_match:
                return self._process_generic_task(file_path, task_content)

            request = content_match.group(1).strip()

            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', request)
            if not email_match:
                return self._process_generic_task(file_path, task_content)

            to_email = email_match.group(0)

            # Create PROFESSIONAL email based on request content
            if 'explain ai' in request.lower() or 'artificial intelligence' in request.lower():
                subject = "Introduction to Artificial Intelligence"
                email_body = """Dear Valued Client,

Thank you for your inquiry about Artificial Intelligence (AI).

AI refers to the simulation of human intelligence in machines programmed to think and learn like humans. Here are the key concepts in three sentences:

1. AI encompasses various technologies including machine learning, natural language processing, and computer vision that enable computers to perform tasks requiring human intelligence.

2. Machine learning, a subset of AI, allows systems to automatically improve from experience without being explicitly programmed, making it possible for applications like recommendation systems and voice assistants.

3. AI is transforming industries worldwide, from healthcare diagnostics to autonomous vehicles, and is expected to contribute significantly to economic growth in the coming decades.

I hope this explanation helps clarify the concept of AI. If you need more detailed information or have specific questions, please don't hesitate to ask.

Best regards,
M. Bashar Sheikh
AI Employee Vault"""

            elif 'greet' in request.lower() or 'hello' in request.lower():
                subject = "Warm Greetings"
                email_body = """Dear Valued Client,

I hope this email finds you well!

I wanted to take a moment to send you warm greetings and let you know that we're here to support you. Your satisfaction is our priority, and we're committed to providing you with the best possible service.

If there's anything we can assist you with or if you have any questions, please feel free to reach out. We're always happy to help!

Wishing you a wonderful day ahead.

Best regards,
M. Bashar Sheikh
AI Employee Vault"""

            elif 'pricing' in request.lower() or 'price' in request.lower() or 'cost' in request.lower():
                subject = "Pricing Information"
                email_body = """Dear Valued Client,

Thank you for your interest in our services!

We offer competitive pricing tailored to meet your specific needs. Our pricing structure is designed to provide maximum value while maintaining the highest quality standards.

Here's a general overview:
- Basic Package: Starting at $500
- Professional Package: Starting at $1,500
- Enterprise Package: Custom pricing based on requirements

Each package includes comprehensive support and customization options. I'd be happy to schedule a call to discuss your specific requirements and provide a detailed quote.

Please let me know your availability for a brief discussion this week.

Best regards,
M. Bashar Sheikh
AI Employee Vault"""

            elif 'meeting' in request.lower() or 'schedule' in request.lower():
                subject = "Meeting Request"
                email_body = """Dear Valued Client,

Thank you for your interest in scheduling a meeting.

I would be delighted to meet with you to discuss your requirements and explore how we can assist you. Here are some available time slots for this week:

- Tuesday, 2:00 PM - 4:00 PM
- Wednesday, 10:00 AM - 12:00 PM
- Thursday, 3:00 PM - 5:00 PM

Please let me know which time works best for you, or feel free to suggest an alternative time that fits your schedule better.

I look forward to our conversation.

Best regards,
M. Bashar Sheikh
AI Employee Vault"""

            else:
                # Generic professional template
                subject = "Re: Your Inquiry"
                email_body = f"""Dear Valued Client,

Thank you for reaching out to us.

Regarding your request: "{request[:100]}"

We appreciate your business and are committed to providing you with the best possible service. Our team is reviewing your inquiry and will get back to you with a detailed response shortly.

If you have any urgent matters or additional questions, please don't hesitate to contact us.

Best regards,
M. Bashar Sheikh
AI Employee Vault"""

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
2. Edit if needed
3. Move to Approved/ to send
4. Move to Rejected/ to cancel
"""

            approval_path.write_text(approval_content, encoding='utf-8')
            logger.info(f"Created email approval: {approval_filename}")

            done_path = self.done_folder / file_path.name
            shutil.move(str(file_path), str(done_path))
            logger.info(f"Moved to Done: {file_path.name}")

            return True

        except Exception as e:
            logger.error(f"Error processing email: {e}")
            return False

    def _process_whatsapp_task(self, file_path: Path, task_content: str) -> bool:
        """Process WhatsApp with PROFESSIONAL template"""
        try:
            import re
            from datetime import datetime

            content_match = re.search(r'## Content\s*\n\n(.+?)(?=\n##|\Z)', task_content, re.DOTALL)
            if not content_match:
                return self._process_generic_task(file_path, task_content)

            request = content_match.group(1).strip()

            phone_match = re.search(r'\+?\d[\d\s-]{8,}', request)
            if not phone_match:
                return self._process_generic_task(file_path, task_content)

            phone = phone_match.group(0).replace(' ', '').replace('-', '')

            # Create PROFESSIONAL WhatsApp message
            if 'follow' in request.lower() or 'reminder' in request.lower():
                message = """Hello! 👋

Hope you're doing well!

This is a friendly follow-up regarding our previous conversation. Just wanted to check in and see if you had any questions or needed any further information.

Please feel free to reach out if there's anything I can assist you with.

Best regards,
M. Bashar Sheikh"""

            elif 'thank' in request.lower() or 'thanks' in request.lower():
                message = """Hello! 👋

Thank you so much for your message!

We truly appreciate your time and interest. Your support means a lot to us.

If there's anything we can help you with, please don't hesitate to ask.

Warm regards,
M. Bashar Sheikh"""

            else:
                message = f"""Hello! 👋

Thank you for reaching out.

Regarding your message: "{request[:80]}"

We'll get back to you shortly with more information.

Best regards,
M. Bashar Sheikh"""

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
1. Review the message above
2. Move to Approved/ to send
"""

            approval_path.write_text(approval_content, encoding='utf-8')
            logger.info(f"Created WhatsApp approval: {approval_filename}")

            done_path = self.done_folder / file_path.name
            shutil.move(str(file_path), str(done_path))
            logger.info(f"Moved to Done: {file_path.name}")

            return True

        except Exception as e:
            logger.error(f"Error processing WhatsApp: {e}")
            return False

    def _process_linkedin_task(self, file_path: Path, task_content: str) -> bool:
        """Process LinkedIn with PROFESSIONAL template"""
        try:
            import re
            from datetime import datetime

            content_match = re.search(r'## Content\s*\n\n(.+?)(?=\n##|\Z)', task_content, re.DOTALL)
            if not content_match:
                return self._process_generic_task(file_path, task_content)

            request = content_match.group(1).strip()

            # Create PROFESSIONAL LinkedIn post
            if 'ai' in request.lower() or 'artificial intelligence' in request.lower():
                post_content = """🚀 The Future is Here: Artificial Intelligence!

AI is no longer science fiction—it's transforming how we work, live, and interact with technology every single day.

From smart assistants to autonomous vehicles, machine learning algorithms to predictive analytics, AI is revolutionizing industries and creating unprecedented opportunities for innovation.

The question isn't whether to embrace AI, but how quickly we can adapt and leverage its potential to drive growth and efficiency.

What's your experience with AI? How is it impacting your industry?

#ArtificialIntelligence #AI #Innovation #Technology #FutureOfWork #MachineLearning #DigitalTransformation"""

            elif 'automation' in request.lower() or 'automate' in request.lower():
                post_content = """⚡ Automation: Working Smarter, Not Harder!

In today's fast-paced business world, automation isn't just a luxury—it's a necessity for staying competitive.

By automating repetitive tasks, businesses can:
✅ Save 40+ hours per week
✅ Reduce human error by 90%
✅ Focus on strategic growth
✅ Improve customer satisfaction

The best part? Automation doesn't replace human creativity—it amplifies it!

What processes have you automated? Share your wins below! 👇

#Automation #Productivity #BusinessGrowth #Efficiency #Innovation #DigitalTransformation"""

            else:
                post_content = f"""💼 Professional Insights

{request}

Key takeaways:
✅ Continuous learning drives success
✅ Innovation leads to growth
✅ Collaboration creates opportunities

What are your thoughts on this? Let's discuss in the comments!

#Professional #Business #Growth #Innovation #Leadership"""

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
1. Review the post above
2. Move to Approved/ to publish
"""

            approval_path.write_text(approval_content, encoding='utf-8')
            logger.info(f"Created LinkedIn approval: {approval_filename}")

            done_path = self.done_folder / file_path.name
            shutil.move(str(file_path), str(done_path))
            logger.info(f"Moved to Done: {file_path.name}")

            return True

        except Exception as e:
            logger.error(f"Error processing LinkedIn: {e}")
            return False

    def _process_odoo_task(self, file_path: Path, task_content: str) -> bool:
        """Process Odoo lead with PROFESSIONAL template"""
        try:
            import re
            from datetime import datetime

            content_match = re.search(r'## Content\s*\n\n(.+?)(?=\n##|\Z)', task_content, re.DOTALL)
            if not content_match:
                return self._process_generic_task(file_path, task_content)

            request = content_match.group(1).strip()

            # Extract lead information
            name_match = re.search(r'name:\s*(.+?)(?:\n|$)', request, re.IGNORECASE)
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', request)
            phone_match = re.search(r'phone:\s*(\+?[\d\s-]{8,})', request, re.IGNORECASE)
            source_match = re.search(r'source:\s*(.+?)(?:\n|$)', request, re.IGNORECASE)

            lead_name = name_match.group(1).strip() if name_match else "Unknown Lead"
            email = email_match.group(0) if email_match else ""
            phone = phone_match.group(1).strip() if phone_match else ""
            source = source_match.group(1).strip() if source_match else "Dashboard"

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

## Next Steps

1. Review the lead information above
2. Edit if needed (update YAML fields)
3. Move to Approved/ to create in Odoo
4. Move to Rejected/ to cancel

---
*This lead will be automatically created in Odoo CRM upon approval*
"""

            approval_path.write_text(approval_content, encoding='utf-8')
            logger.info(f"Created Odoo approval: {approval_filename}")

            done_path = self.done_folder / file_path.name
            shutil.move(str(file_path), str(done_path))
            logger.info(f"Moved to Done: {file_path.name}")

            return True

        except Exception as e:
            logger.error(f"Error processing Odoo: {e}")
            return False

    def _process_generic_task(self, file_path: Path, task_content: str) -> bool:
        """Process generic task"""
        try:
            import re
            from datetime import datetime

            content_match = re.search(r'## Content\s*\n\n(.+?)(?=\n##|\Z)', task_content, re.DOTALL)
            request = content_match.group(1).strip() if content_match else "No content"

            filename_lower = file_path.name.lower()
            request_lower = request.lower()

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

            # Detect task type and create appropriate approval
            if 'linkedin' in filename_lower or 'linkedin' in request_lower or 'post' in request_lower:
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
            elif 'email' in filename_lower or 'email' in request_lower:
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
            logger.info(f"Created approval: {approval_filename}")

            done_path = self.done_folder / file_path.name
            shutil.move(str(file_path), str(done_path))
            logger.info(f"Moved to Done: {file_path.name}")

            return True

        except Exception as e:
            logger.error(f"Error processing generic task: {e}")
            return False

    def _detect_task_type(self, filename: str, content: str) -> str:
        """Detect task type"""
        filename_lower = filename.lower()
        content_lower = content.lower()

        # Odoo detection
        if any(kw in content_lower for kw in ['odoo', 'lead', 'crm', 'invoice', 'quotation']):
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
            if re.search(r'[\w\.-]+@[\w\.-]+\.\w+', content):
                return 'inbox_email'
            if re.search(r'\+?\d[\d\s-]{8,}', content):
                return 'inbox_whatsapp'
            if any(kw in content_lower for kw in ['post', 'linkedin', 'social media']):
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
