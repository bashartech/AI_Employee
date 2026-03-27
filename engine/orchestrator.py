"""
Orchestrator module
Main automation engine that coordinates task processing with Claude Code
Enhanced with Knowledge Base for Customer Support AI and HR Hiring Automation
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
from services.knowledge_base import KnowledgeBaseService
from services.hr_resume_parser import ResumeParser
from services.hr_candidate_tracker import CandidateTracker
from services.hr_resume_doc_creator import ResumeDocCreator
from services.hr_interview_scheduler import InterviewScheduler


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

        # Email signature configuration
        self.sender_name = "M. Bashar Sheikh"  # Your name for email signatures

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
            elif task_type == 'support_ticket':
                return self._process_support_ticket_task(file_path, task_content)
            elif task_type == 'hr_application':  # NEW! HR Hiring Automation
                return self._process_hr_application(file_path, task_content)
            elif task_type == 'inbox_whatsapp':
                return self._process_inbox_whatsapp_task(file_path, task_content)
            elif task_type == 'inbox_linkedin':
                return self._process_inbox_linkedin_task(file_path, task_content)
            elif task_type == 'inbox_facebook':
                return self._process_facebook_task(file_path, task_content)
            elif task_type == 'facebook_comment':
                return self._process_facebook_comment_task(file_path, task_content)
            elif task_type == 'twitter':  # NEW!
                return self._process_twitter_task(file_path, task_content)
            elif task_type == 'inbox':
                return self._process_generic_inbox_task(file_path, task_content)
            elif task_type == 'whatsapp':
                return self._process_whatsapp_task(file_path, task_content)
            elif task_type == 'linkedin':
                return self._process_linkedin_task(file_path, task_content)
            elif task_type == 'facebook':
                return self._process_facebook_task(file_path, task_content)
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

    def _process_support_ticket_task(self, file_path: Path, task_content: str) -> bool:
        """Process Customer Support AI ticket - Create ticket, Google Doc, Sheets entry, and approval file"""
        try:
            import re
            from datetime import datetime
            import subprocess

            logger.info(f"🎫 Processing Customer Support ticket: {file_path.name}")

            # Extract email details
            from_match = re.search(r'from:\s*(.+)', task_content, re.IGNORECASE)
            from_email = from_match.group(1).strip() if from_match else "unknown@example.com"
            
            subject_match = re.search(r'subject:\s*(.+)', task_content, re.IGNORECASE)
            subject = subject_match.group(1).strip() if subject_match else "Support Request"
            
            # Extract email content
            content_match = re.search(r'## Email Content\s*\n\n(.+?)(?=\n##|\Z)', task_content, re.DOTALL)
            email_body = content_match.group(1).strip() if content_match else task_content

            # Categorize the support request
            category = self._categorize_support_request(subject, email_body)
            
            # Generate ticket ID
            ticket_id = f"SUP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            logger.info(f"  Category: {category}")
            logger.info(f"  Ticket ID: {ticket_id}")

            # Create support ticket file
            self._create_support_ticket_file(ticket_id, from_email, subject, email_body, category)
            
            # Create Google Doc for ticket (if Google services available)
            doc_link = self._create_support_ticket_doc(ticket_id, from_email, subject, email_body, category)
            
            # Log to Google Sheets (if available)
            self._log_support_ticket_to_sheets(ticket_id, from_email, subject, category, doc_link)
            
            # Generate AI response using Claude
            ai_response = self._generate_support_response(category, subject, email_body, ticket_id)

            # Create approval file for sending response
            self._create_support_approval_file(ticket_id, from_email, subject, ai_response, category, doc_link)

            # Move original to Done
            done_path = self.done_folder / file_path.name
            shutil.move(str(file_path), str(done_path))

            logger.info(f"✅ Support ticket processed: {ticket_id}")
            logger.info(f"📁 Approval file created in Pending Approval folder")
            logger.info(f"💡 Move approval file to Approved/ folder to send email")
            logger.info(f"💡 Run 'python execute_approved.py' to auto-send approved emails")
            return True

        except Exception as e:
            logger.error(f"❌ Error processing support ticket: {e}")
            return False

    def _process_hr_application(self, file_path: Path, task_content: str) -> bool:
        """Process HR job application - Parse resume, score candidate, create docs, schedule interview"""
        try:
            import re
            from datetime import datetime

            logger.info(f"💼 Processing HR application: {file_path.name}")

            # Extract applicant info from YAML frontmatter
            from_match = re.search(r'from:\s*(.+)', task_content, re.IGNORECASE)
            from_email = from_match.group(1).strip() if from_match else "unknown@example.com"
            
            subject_match = re.search(r'subject:\s*(.+)', task_content, re.IGNORECASE)
            subject = subject_match.group(1).strip() if subject_match else "Job Application"
            
            # Extract resume file paths
            resume_files_match = re.search(r'resume_files:\s*\[(.+?)\]', task_content)
            resume_files = []
            if resume_files_match:
                resume_files_str = resume_files_match.group(1)
                resume_files = [f.strip().strip("'\"") for f in resume_files_str.split(',') if f.strip()]
            
            # Extract email body content (resume might be in email body)
            email_content_match = re.search(r'## Email Content.*?##', task_content, re.DOTALL)
            email_body = ""
            if email_content_match:
                email_body = email_content_match.group(0).strip()
                # Remove the "## Email Content" header
                email_body = re.sub(r'^## Email Content.*?\n', '', email_body, flags=re.DOTALL).strip()
            
            logger.info(f"  Applicant: {from_email}")
            logger.info(f"  Position: {subject}")
            logger.info(f"  Resumes: {len(resume_files)} file(s)")
            logger.info(f"  Email body: {len(email_body)} chars")

            # Initialize HR services
            resume_parser = ResumeParser()
            candidate_tracker = CandidateTracker()
            doc_creator = ResumeDocCreator()
            interview_scheduler = InterviewScheduler()

            # Process resume from file OR email body
            candidate_data = None
            
            if resume_files:
                # Process resume from file
                for resume_path_str in resume_files:
                    resume_path = Path(resume_path_str)
                    if not resume_path.exists():
                        logger.warning(f"⚠️ Resume file not found: {resume_path}")
                        continue

                    logger.info(f"  📄 Parsing resume: {resume_path.name}")

                    # Parse resume
                    parse_result = resume_parser.parse_file(resume_path)

                    if not parse_result.get('success'):
                        logger.error(f"❌ Failed to parse resume: {parse_result.get('error')}")
                        continue

                    candidate_data = parse_result
                    candidate_data['from_email'] = from_email
                    candidate_data['subject'] = subject
                    candidate_data['resume_file'] = str(resume_path)
                    candidate_data['position'] = subject

                    logger.info(f"  ✅ Resume parsed successfully")
                    logger.info(f"  Score: {candidate_data.get('score', {}).get('total', 0)}/100 (Grade: {candidate_data.get('score', {}).get('grade', 'N/A')})")
                    logger.info(f"  Recommendation: {candidate_data.get('recommendation', {}).get('message', 'N/A')}")
                    
                    break  # Process first valid resume
                    
            elif email_body:
                # Process resume from email body
                logger.info(f"  📄 Parsing resume from email body...")
                
                parse_result = resume_parser.parse_text(email_body, source=str(file_path))
                
                if not parse_result.get('success'):
                    logger.error(f"❌ Failed to parse resume from email: {parse_result.get('error')}")
                    return False
                
                candidate_data = parse_result
                candidate_data['from_email'] = from_email
                candidate_data['subject'] = subject
                candidate_data['resume_file'] = 'email_body'
                candidate_data['position'] = subject
                
                logger.info(f"  ✅ Resume parsed from email body successfully")
                logger.info(f"  Name: {candidate_data.get('candidate', {}).get('name', 'Unknown')}")
                logger.info(f"  Email: {candidate_data.get('candidate', {}).get('email', 'N/A')}")
                logger.info(f"  Score: {candidate_data.get('score', {}).get('total', 0)}/100 (Grade: {candidate_data.get('score', {}).get('grade', 'N/A')})")
                logger.info(f"  Recommendation: {candidate_data.get('recommendation', {}).get('message', 'N/A')}")
            else:
                logger.warning(f"⚠️ No resume files or email body content for {from_email}")
                return False
            
            if not candidate_data:
                logger.error(f"❌ No candidate data extracted")
                return False

            # Add to candidate tracker (Google Sheets)
            logger.info(f"  📊 Logging to Google Sheets...")
            tracker_result = candidate_tracker.add_candidate(candidate_data)
            if tracker_result.get('success'):
                logger.info(f"  ✅ Candidate logged to tracker: {tracker_result.get('candidate_id')}")
            else:
                logger.warning(f"  ⚠️ Failed to log to tracker: {tracker_result.get('error')}")

            # Create Google Doc for candidate
            logger.info(f"  📝 Creating Google Doc...")
            resume_text = email_body if candidate_data.get('resume_file') == 'email_body' else ""
            doc_result = doc_creator.create_candidate_doc(candidate_data, resume_text)
            if doc_result.get('success'):
                logger.info(f"  ✅ Google Doc created: {doc_result.get('doc_link')}")
                candidate_data['doc_link'] = doc_result.get('doc_link')
            else:
                logger.warning(f"  ⚠️ Failed to create doc: {doc_result.get('error')}")

            # Check if candidate should be interviewed (score >= 80)
            score = candidate_data.get('score', {}).get('total', 0)
            if score >= 80:
                logger.info(f"  🎯 High-score candidate (Score: {score}) - Scheduling interview...")
                
                # Schedule interview
                interview_result = interview_scheduler.schedule_interview(candidate_data)
                if interview_result.get('success'):
                    logger.info(f"  ✅ Interview scheduled: {interview_result.get('interview_datetime')}")
                    logger.info(f"  🔗 Meet link: {interview_result.get('meet_link')}")
                    
                    # Update candidate tracker with interview details
                    candidate_tracker.schedule_interview(
                        tracker_result.get('candidate_id'),
                        interview_result.get('interview_datetime'),
                        interview_result.get('meet_link')
                    )
                    
                    # Create approval file for sending interview invitation
                    self._create_interview_approval_file(
                        candidate_data,
                        interview_result,
                        tracker_result.get('candidate_id')
                    )
                else:
                    logger.warning(f"  ⚠️ Failed to schedule interview: {interview_result.get('error')}")
            else:
                logger.info(f"  ℹ️ Score {score} < 80 - No interview needed")
                # Create approval for rejection email
                self._create_rejection_approval_file(candidate_data, tracker_result.get('candidate_id'))

            # Move original HR application to Done
            done_path = self.done_folder / file_path.name
            shutil.move(str(file_path), str(done_path))
            logger.info(f"✅ HR application processed: {file_path.name}")
            logger.info(f"📁 Moved to Done folder")

            return True

        except Exception as e:
            logger.error(f"❌ Error processing HR application: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def _create_rejection_approval_file(self, candidate_data: Dict, candidate_id: str):
        """Create approval file for sending rejection email"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            approval_filename = f"APPROVAL_rejection_{candidate_data.get('candidate', {}).get('name', 'Unknown').replace(' ', '_')}_{timestamp}.md"
            approval_path = self.pending_approval_folder / approval_filename

            approval_content = f"""---
type: email_approval
action: send_email
to: {candidate_data.get('from_email', '')}
subject: Re: {candidate_data.get('subject', 'Job Application')}
candidate_id: {candidate_id}
candidate_name: {candidate_data.get('candidate', {}).get('name', 'Unknown')}
score: {candidate_data.get('score', {}).get('total', 0)}
---

# Rejection Email Approval

## Candidate Details
- **Name:** {candidate_data.get('candidate', {}).get('name', 'Unknown')}
- **Email:** {candidate_data.get('from_email', '')}
- **Position:** {candidate_data.get('position', 'Position')}
- **Score:** {candidate_data.get('score', {}).get('total', 0)}/100

## Email Body

Dear {candidate_data.get('candidate', {}).get('name', 'Candidate')},

Thank you for your interest in the {candidate_data.get('position', 'position')} position at TechCorp Solutions.

We appreciate you taking the time to apply and share your background with us. While your qualifications are impressive, we have decided to move forward with other candidates whose experience more closely matches our current needs.

We will keep your application on file and reach out if a suitable position opens up in the future.

We wish you the best in your job search.

Best regards,
{self.sender_name}
Talent Acquisition Team
TechCorp Solutions

---

## Instructions
1. **Review** the rejection email above
2. **Edit** if needed
3. **Approve:** Move to `Approved/` folder to send
4. **Reject:** Move to `Rejected/` folder if not ready

## Notes
- This is a polite rejection email
- Candidate was scored {candidate_data.get('score', {}).get('total', 0)}/100
- Response will be sent automatically upon approval
"""

            approval_path.write_text(approval_content, encoding='utf-8')
            logger.info(f"  ✅ Rejection approval file created: {approval_filename}")
            
        except Exception as e:
            logger.error(f"  ❌ Error creating rejection approval file: {e}")

    def _create_interview_approval_file(self, candidate_data: Dict, interview_result: Dict, candidate_id: str):
        """Create approval file for sending interview invitation email"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            approval_filename = f"APPROVAL_interview_{candidate_data.get('name', 'Unknown').replace(' ', '_')}_{timestamp}.md"
            approval_path = self.pending_approval_folder / approval_filename

            approval_content = f"""---
type: email_approval
action: send_email
to: {candidate_data.get('from_email', '')}
subject: Interview Invitation - {candidate_data.get('position', 'Position')}
candidate_id: {candidate_id}
candidate_name: {candidate_data.get('name', 'Unknown')}
position: {candidate_data.get('position', 'Position')}
score: {candidate_data.get('score', {}).get('total', 0)}
grade: {candidate_data.get('score', {}).get('grade', 'N/A')}
---

# Interview Invitation Approval

## Candidate Details
- **Name:** {candidate_data.get('name', 'Unknown')}
- **Email:** {candidate_data.get('from_email', '')}
- **Position:** {candidate_data.get('position', 'Position')}
- **Score:** {candidate_data.get('score', {}).get('total', 0)}/100 (Grade: {candidate_data.get('score', {}).get('grade', 'N/A')})
- **Candidate ID:** {candidate_id}

## Interview Details
- **Date/Time:** {interview_result.get('interview_datetime', 'TBD')}
- **Format:** Video Call (Google Meet)
- **Duration:** 45 minutes
- **Meet Link:** {interview_result.get('meet_link', '')}

## Email Body

Dear {candidate_data.get('name', 'Candidate')},

Thank you for your interest in the {candidate_data.get('position', 'position')} position at TechCorp Solutions.

We were impressed by your background and would like to invite you for an interview.

─────────────────────────────
INTERVIEW DETAILS
─────────────────────────────
Position: {candidate_data.get('position', 'Position')}
Format: Video Call (Google Meet)
Duration: 45 minutes

📅 Date: {interview_result.get('interview_datetime', 'TBD')}
🔗 Meeting Link: {interview_result.get('meet_link', '')}
─────────────────────────────

Please confirm your availability by replying to this email.

If you need to reschedule, please let us know at least 24 hours in advance.

We look forward to speaking with you!

Best regards,
{self.sender_name}
Talent Acquisition Team
TechCorp Solutions

📧 careers@techcorp.com
📞 +1 (555) 123-4567

---

## Instructions
1. **Review** the interview details above
2. **Edit** if needed (date/time, message)
3. **Approve:** Move to `Approved/` folder to send
4. **Reject:** Move to `Rejected/` folder if not ready

## Notes
- Interview was automatically scheduled based on candidate's high score ({candidate_data.get('score', {}).get('total', 0)}/100)
- Google Meet link was auto-generated
- Candidate has been logged to HR Candidates Tracker
"""

            approval_path.write_text(approval_content, encoding='utf-8')
            logger.info(f"  ✅ Interview approval file created: {approval_filename}")
            
        except Exception as e:
            logger.error(f"  ❌ Error creating interview approval file: {e}")

    def _categorize_support_request(self, subject: str, body: str) -> str:
        """Categorize support request by urgency and type"""
        text = (subject + " " + body).lower()
        
        # Check for urgent keywords
        urgent_keywords = ['urgent', 'asap', 'emergency', 'critical', 'down', 'broken', 'not working', 'immediately']
        if any(keyword in text for keyword in urgent_keywords):
            return 'urgent'
        
        # Check for billing keywords
        billing_keywords = ['invoice', 'payment', 'billing', 'refund', 'charge', 'price', 'cost', 'money']
        if any(keyword in text for keyword in billing_keywords):
            return 'billing'
        
        # Check for technical keywords
        technical_keywords = ['bug', 'error', 'issue', 'problem', 'technical', 'help', 'support', 'broken']
        if any(keyword in text for keyword in technical_keywords):
            return 'technical'
        
        # Check for feature request
        feature_keywords = ['feature', 'request', 'suggestion', 'improvement', 'idea', 'add']
        if any(keyword in text for keyword in feature_keywords):
            return 'feature'
        
        return 'general'

    def _create_support_ticket_file(self, ticket_id: str, from_email: str, subject: str, body: str, category: str):
        """Create support ticket file in Support_Tickets folder"""
        try:
            from pathlib import Path as FilePath
            support_tickets_dir = FilePath(__file__).parent.parent / "Support_Tickets"
            support_tickets_dir.mkdir(exist_ok=True)
            
            ticket_content = f"""---
type: support_ticket
ticket_id: {ticket_id}
category: {category}
priority: {'high' if category == 'urgent' else 'normal'}
customer_email: {from_email}
subject: {subject}
created: {datetime.now().isoformat()}
status: new
---

# Support Ticket: {ticket_id}

## Customer Information
- **Email:** {from_email}
- **Category:** {category.title()}
- **Priority:** {'High ⚠️' if category == 'urgent' else 'Normal'}
- **Created:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Original Email
**Subject:** {subject}

**Content:**
{body}

## Resolution
[To be filled by support agent]

## Notes
[Add notes here]
"""
            
            ticket_file = support_tickets_dir / f"{ticket_id}.md"
            ticket_file.write_text(ticket_content, encoding='utf-8')
            logger.info(f"  📄 Ticket file created: {ticket_file.name}")
            
        except Exception as e:
            logger.error(f"  ❌ Error creating ticket file: {e}")

    def _create_support_ticket_doc(self, ticket_id: str, from_email: str, subject: str, body: str, category: str) -> str:
        """Create Google Doc for support ticket"""
        try:
            from services.google import GoogleDocsService, GoogleDriveService
            
            docs = GoogleDocsService()
            
            # Create document
            doc_title = f"Support Ticket {ticket_id} - {from_email}"
            doc_content = f"""
SUPPORT TICKET: {ticket_id}
=====================================

Customer: {from_email}
Category: {category.title()}
Priority: {'HIGH' if category == 'urgent' else 'Normal'}
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Subject: {subject}

ORIGINAL ISSUE:
{body}

RESOLUTION:
[To be filled by support agent]

NOTES:
[Add notes here]
"""
            
            result = docs.create_document(doc_title, doc_content)
            
            if result['success']:
                # Try different keys for the link
                doc_link = result.get('link') or result.get('document', {}).get('webViewLink') or result.get('webViewLink') or ''
                logger.info(f"  📄 Google Doc created: {doc_link if doc_link else 'No link returned'}")
                return doc_link
            
            return ''
            
        except Exception as e:
            logger.error(f"  ❌ Error creating Google Doc: {e}")
            return ''

    def _log_support_ticket_to_sheets(self, ticket_id: str, from_email: str, subject: str, category: str, doc_link: str):
        """Log support ticket to Google Sheets tracker"""
        try:
            from services.google import GoogleSheetsService
            
            sheets = GoogleSheetsService()
            
            # Ticket data row
            ticket_row = [
                ticket_id,
                from_email,
                subject[:50] + '...' if len(subject) > 50 else subject,
                category.title(),
                'High' if category == 'urgent' else 'Normal',
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'New',  # Status
                doc_link or 'N/A'
            ]
            
            # Try to get or create the spreadsheet
            try:
                # Get or create "Support Tickets Tracker" spreadsheet
                result = sheets.get_or_create_spreadsheet('Support Tickets Tracker')
                
                if result['success']:
                    spreadsheet_id = result['id']
                    
                    # Append data to sheet
                    append_result = sheets.append_data(spreadsheet_id, 'Sheet1!A1', [ticket_row])
                    
                    if append_result['success']:
                        logger.info(f"  📊 Logged to Google Sheets: {result.get('link', 'N/A')}")
                    else:
                        logger.warning(f"  ⚠️ Could not append to sheet: {append_result.get('error', 'Unknown error')}")
                else:
                    logger.warning(f"  ⚠️ Could not create/find spreadsheet: {result.get('error', 'Unknown error')}")
                    
            except Exception as sheet_error:
                logger.warning(f"  ⚠️ Sheets error: {sheet_error}")
                logger.info(f"  ℹ️ Google Sheets logging skipped - will retry next time")
            
        except Exception as e:
            logger.error(f"  ❌ Error logging to Sheets: {e}")

    def _get_support_tickets_spreadsheet_id(self):
        """Get spreadsheet ID for Support Tickets Tracker"""
        try:
            from services.google import GoogleSheetsService
            
            sheets = GoogleSheetsService()
            
            # List all spreadsheets and find "Support Tickets Tracker"
            all_spreadsheets = sheets.list_spreadsheets()
            
            if all_spreadsheets and 'spreadsheets' in all_spreadsheets:
                for spreadsheet in all_spreadsheets['spreadsheets']:
                    if spreadsheet.get('properties', {}).get('title') == 'Support Tickets Tracker':
                        spreadsheet_id = spreadsheet.get('spreadsheetId')
                        logger.info(f"  ✅ Found Support Tickets Tracker: {spreadsheet_id}")
                        return spreadsheet_id
            
            return None
            
        except Exception as e:
            logger.error(f"  ❌ Error finding spreadsheet: {e}")
            return None

    def _generate_support_response(self, category: str, subject: str, body: str, ticket_id: str) -> str:
        """Generate AI response for support ticket using Claude"""
        try:
            # Define response templates
            templates = {
                'urgent': f"""Dear Valued Customer,

Thank you for contacting us regarding this URGENT matter.

We understand the critical nature of your issue and have escalated it to our senior support team.

Ticket ID: {ticket_id}
Priority: URGENT
Estimated Response: Within 1 hour

A senior engineer will contact you shortly.

Best regards,
{self.sender_name}
Customer Support Team""",

                'billing': f"""Dear Valued Customer,

Thank you for your inquiry regarding billing.

Our billing specialist has received your request and will review your account shortly.

Ticket ID: {ticket_id}
Priority: Normal
Estimated Response: Within 4 hours during business hours

Best regards,
{self.sender_name}
Billing Support Team""",

                'technical': f"""Dear Valued Customer,

Thank you for contacting technical support.

We've received your request and a support engineer will investigate this issue.

Ticket ID: {ticket_id}
Priority: Normal
Estimated Response: Within 24 hours

Best regards,
{self.sender_name}
Technical Support Team""",

                'feature': f"""Dear Valued Customer,

Thank you for your feature suggestion! We appreciate customers like you who help us improve.

Your feedback has been forwarded to our product team for consideration.

Ticket ID: {ticket_id}
Status: Under Review

Best regards,
{self.sender_name}
Product Team""",

                'general': f"""Dear Valued Customer,

Thank you for contacting us.

We've received your inquiry and will respond as soon as possible.

Ticket ID: {ticket_id}
Priority: Normal
Estimated Response: Within 24 hours

Best regards,
{self.sender_name}
Customer Support Team"""
            }
            
            return templates.get(category, templates['general'])
            
        except Exception as e:
            logger.error(f"  ❌ Error generating response: {e}")
            return f"""Dear Customer,

Thank you for contacting us.

Ticket ID: {ticket_id}

We will respond to your inquiry shortly.

Best regards,
{self.sender_name}"""

    def _create_support_approval_file(self, ticket_id: str, to_email: str, subject: str, response: str, category: str, doc_link: str):
        """Create approval file for sending support response"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            # Short filename format for better Windows display
            approval_filename = f"APPROVAL_email_{timestamp}.md"
            approval_path = self.pending_approval_folder / approval_filename

            approval_content = f"""---
type: email_approval
action: send_email
to: {to_email}
subject: {subject}
ticket_id: {ticket_id}
category: {category}
---

# Email Response Approval

## Customer Details
- **Email:** {to_email}
- **Ticket ID:** {ticket_id}
- **Category:** {category.title()}
- **Priority:** {'High ⚠️' if category == 'urgent' else 'Normal'}

## AI-Generated Response

## Email Body

{response}

---

## Instructions
1. **Review** the AI-generated response above
2. **Edit** if needed for personalization
3. **Approve:** Move to `Approved/` folder to send
4. **Reject:** Move to `Rejected/` folder if manual response needed

## Notes
- This is an AI-generated auto-response
- For urgent tickets, consider personal follow-up
- Response will be sent automatically upon approval
- Google Doc: {doc_link if doc_link else 'N/A'}
"""

            approval_path.write_text(approval_content, encoding='utf-8')
            logger.info(f"  ✅ Approval file created: {approval_filename}")
            
        except Exception as e:
            logger.error(f"  ❌ Error creating approval file: {e}")

    def _process_inbox_email_task(self, file_path: Path, task_content: str) -> bool:
        """Process inbox email composition task - Uses Claude to generate professional email"""
        try:
            import re
            from datetime import datetime
            import subprocess

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

            # Use Claude to generate professional email
            logger.info(f"🤖 Generating email with Claude...")
            
            claude_prompt = f"""
You are a professional email assistant.

Generate a professional email response based on this request:
"{request}"

Topic: {topic}
Recipient: {to_email}

Requirements:
- Professional and polite tone
- Clear and concise
- Include proper greeting and closing
- Keep it under 200 words
- Focus on being helpful

Output ONLY the email body, nothing else.
"""
            
            try:
                # Use full path to claude executable
                claude_path = r"C:\Users\H P\AppData\Roaming\npm\claude.cmd"
                
                # Run claude with prompt via stdin
                result = subprocess.run(
                    [claude_path, '-p'],
                    input=claude_prompt,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    shell=True
                )
                
                # Debug: log what we got
                if result.stdout:
                    logger.info(f"Claude output length: {len(result.stdout)}")
                if result.stderr:
                    logger.warning(f"Claude stderr: {result.stderr[:200]}")
                
                email_body = result.stdout.strip()
                
                # If Claude fails or returns empty, use fallback
                if not email_body or len(email_body) < 20:
                    email_body = f"""Dear Recipient,

Thank you for reaching out regarding {topic}.

I would be happy to help you with this. Please let me know if you need any additional information or clarification.

Best regards,
{self.sender_name}"""
                    logger.warning(f"Claude returned empty, using fallback")
                
                logger.info(f"✅ Email generated: {email_body[:50]}...")
                
            except subprocess.TimeoutExpired:
                logger.warning(f"Claude timed out after 120 seconds, using fallback")
                email_body = f"""Dear Recipient,

Thank you for reaching out regarding {topic}.

I would be happy to help you with this. Please let me know if you need any additional information.

Best regards,
{self.sender_name}"""
            except Exception as e:
                logger.warning(f"Claude email generation failed: {e}, using fallback")
                email_body = f"""Dear Recipient,

Thank you for reaching out regarding {topic}.

I would be happy to help you with this. Please let me know if you need any additional information.

Best regards,
{self.sender_name}"""

            # Create approval file
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            approval_filename = f"APPROVAL_send_email.md"
            # approval_filename = f"APPROVAL_send_email_{timestamp}.md"
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

## AI-Generated Email Body

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
        """Process generic inbox task - create proper approval file for Claude Code"""
        try:
            import re
            from datetime import datetime

            # Extract the content
            content_match = re.search(r'## Content\s*\n\n(.+?)(?=\n##|\Z)', task_content, re.DOTALL)

            if content_match:
                request = content_match.group(1).strip()
            else:
                request = "No content found"

            # Detect task type from filename or content
            filename_lower = file_path.name.lower()
            request_lower = request.lower()
            
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            
            # Detect LinkedIn post request
            is_linkedin = ('linkedin' in filename_lower or 'linkedin' in request_lower or
                          'post' in filename_lower or 'post' in request_lower)
            
            # Detect email request
            is_email = ('email' in filename_lower or 'email' in request_lower or
                       'mail' in filename_lower or 'reply' in request_lower)
            
            # Detect WhatsApp request
            is_whatsapp = ('whatsapp' in filename_lower or 'whatsapp' in request_lower or
                          'sms' in filename_lower or 'message' in request_lower)

            # Create appropriate approval file based on detected type
            if is_linkedin:
                # Create LinkedIn post approval file
                approval_filename = f"APPROVAL_linkedin_post_{timestamp}.md"
                approval_path = self.pending_approval_folder / approval_filename

                # Generate LinkedIn post content
                post_content = self._generate_linkedin_post(request)

                approval_content = f"""---
type: linkedin_approval
action: linkedin_post
---

# LinkedIn Post Approval

## Original Request
**File:** {file_path.name}
**Request:** {request}

## Post Content

{post_content}

---

## Instructions
1. **Review** the drafted post above
2. **Edit** if needed (add image path, modify content)
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder

**Note:** Once approved, execute_approved.py will automatically publish this post.
"""

            elif is_email:
                # Create email approval file
                approval_filename = f"APPROVAL_send_email.md"
                # approval_filename = f"APPROVAL_send_email_{timestamp}.md"
                approval_path = self.pending_approval_folder / approval_filename

                approval_content = f"""---
type: email_approval
action: send_email
to: recipient@example.com
subject: Response to your inquiry
---

# Email Response Approval

## Original Request
**File:** {file_path.name}
**Request:** {request}

## Email Body

Dear Recipient,

Thank you for reaching out. This is a draft response based on the following request:

{request}

Please let us know if you need any further assistance.

Best regards,
{self.sender_name}

---

## Instructions
1. **Review** the drafted email above
2. **Edit** recipient email, subject, and body as needed
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder

**Note:** Once approved, execute_approved.py will automatically send this email.
"""

            elif is_whatsapp:
                # Create WhatsApp approval file
                approval_filename = f"APPROVAL_send_whatsapp_{timestamp}.md"
                approval_path = self.pending_approval_folder / approval_filename

                approval_content = f"""---
type: whatsapp_approval
action: send_whatsapp
phone: +1234567890
---

# WhatsApp Message Approval

## Original Request
**File:** {file_path.name}
**Request:** {request}

## WhatsApp Message

Hello! 

This is a message based on the following request:

{request}

Please let us know if you need any further assistance.

Best regards,
{self.sender_name}

---

## Instructions
1. **Review** the drafted message above
2. **Edit** phone number and message as needed
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder

**Note:** Once approved, execute_approved.py will automatically send this message.
"""

            else:
                # Generic task - create a task file for Claude Code to process
                # Use APPROVAL_ prefix so it's detected by execute_approved.py patterns
                approval_filename = f"APPROVAL_task_review_{timestamp}.md"
                approval_path = self.pending_approval_folder / approval_filename

                approval_content = f"""---
type: task_approval
action: review_required
original_file: {file_path.name}
---

# Task Review Required

## Original Task
**File:** {file_path.name}

## Content
{request}

---

## Suggested Actions

Please review this task and determine appropriate action:

- [ ] Is this a LinkedIn post request? → Generate post content
- [ ] Is this an email reply? → Draft email response
- [ ] Is this a WhatsApp message? → Draft message
- [ ] Does this require Odoo action? → Create lead/invoice/quotation
- [ ] Other action? → Specify below

## Notes for Claude Code

Please process this task according to the skills in .claude/skills/ directory.
Create appropriate approval file based on the task type.

---

## Instructions
1. **Review** the content above
2. **Claude Code should process this** and create appropriate approval file
3. **Human:** Move to `Done/` when complete
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
            logger.error(f"Error processing generic inbox task: {e}")
            return False

    def _generate_linkedin_post(self, request: str) -> str:
        """Generate a professional LinkedIn post based on request"""
        
        # Check if request mentions specific topics
        request_lower = request.lower()
        
        # Default professional post structure
        post = f"""Excited to share some insights on this topic!

{request}

Key takeaways:
✅ Professional development is essential
✅ Continuous learning drives success
✅ Innovation leads to growth

What are your thoughts on this? Let me know in the comments!

#Professional #Business #Growth #Innovation #Leadership"""

        # Customize based on detected topics
        if any(keyword in request_lower for keyword in ['full stack', 'fullstack', 'development', 'developer']):
            post = f"""🚀 Full Stack Development Insights

{request}

The world of full stack development continues to evolve with:
✅ Modern frontend frameworks (React, Vue, Angular)
✅ Robust backend technologies (Node.js, Python, Go)
✅ Cloud-native architectures
✅ AI/ML integration

As developers, staying current with both frontend and backend technologies is crucial for building scalable, efficient applications.

What's your favorite full stack technology right now?

#FullStack #Development #WebDevelopment #Coding #Tech #Programming #AI #Innovation"""

        elif any(keyword in request_lower for keyword in ['ai', 'artificial intelligence', 'machine learning', 'ml']):
            post = f"""🤖 AI & Development Revolution

{request}

The integration of AI in development is transforming how we build software:
✅ AI-assisted coding (Copilot, Codeium)
✅ Automated testing and debugging
✅ Intelligent code review
✅ Natural language interfaces

The future of development is human-AI collaboration!

How are you leveraging AI in your development workflow?

#AI #MachineLearning #Development #Innovation #Tech #FutureOfWork #Automation"""

        elif any(keyword in request_lower for keyword in ['linkedin', 'post', 'content', 'social']):
            post = f"""📝 Content Creation & Professional Branding

{request}

Building a strong professional presence requires:
✅ Consistent, valuable content
✅ Authentic engagement
✅ Industry insights and expertise
✅ Community building

Your professional brand is your digital handshake!

What content strategy works best for you?

#LinkedIn #PersonalBranding #ContentCreation #Professional #Networking #Growth"""

        return post

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
{self.sender_name}"""
        else:
            return f"""Hi there,

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
{self.sender_name}"""

    def _process_email_task(self, file_path: Path, task_content: str) -> bool:
        """Process email task - Check if it's a general inquiry (auto-respond) or needs approval"""
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

            # Parse subject
            subject_match = re.search(r'subject:\s*([^\n]*)', task_content)
            subject = subject_match.group(1).strip() if subject_match and subject_match.group(1).strip() else "(no subject)"

            # Extract email content
            content_match = re.search(r'## Email Content\s*\n\n(.+?)(?=\n##|\Z)', task_content, re.DOTALL)

            if not content_match:
                logger.error("Could not parse email content")
                return False

            original_content = content_match.group(1).strip()

            # Initialize Knowledge Base
            kb = KnowledgeBaseService()
            
            # Classify the query
            query = f"{subject} {original_content}"
            classification = kb.classify_query(query)
            
            logger.info(f"📧 Email classification: {classification['type']} (confidence: {classification['confidence']})")
            
            # Generate response based on classification
            if classification['type'] == 'general_inquiry':
                # Try to get answer from knowledge base
                kb_result = kb.get_answer(query)
                
                if kb_result['found'] and kb_result['confidence'] >= 0.5:
                    # High confidence - generate professional auto-response
                    logger.info(f"✅ Found answer in KB (confidence: {kb_result['confidence']})")
                    
                    # Generate professional response using KB data
                    response_body = self._generate_kb_response(query, kb_result, to_email)
                    
                    # For high confidence auto-responses, send directly (no approval needed)
                    if kb_result['confidence'] >= 0.7:
                        logger.info(f"🚀 High confidence - sending auto-response")
                        return self._send_auto_response_email(to_email, subject, response_body, kb_result)
            
            # For support tickets or low confidence, create approval file
            logger.info(f"📋 Creating approval file for human review")
            response_body = f"""Hi,

Thank you for reaching out. I'm doing well, thank you for asking. How can I assist you today?

Best regards,
{self.sender_name}"""

            # Create approval file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
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

    def _generate_kb_response(self, query: str, kb_result: Dict, to_email: str) -> str:
        """Generate professional response using knowledge base data"""
        try:
            # Extract key information from KB result
            sources = kb_result.get('sources', [])
            top_result = kb_result.get('top_result', {})
            
            # Build professional response
            response = f"""Dear Valued Customer,

Thank you for your inquiry. Based on our records, here's the information you requested:

─────────────────────────────
{kb_result['answer'][:800]}{'...' if len(kb_result['answer']) > 800 else ''}
─────────────────────────────

"""
            # Add sources if available
            if sources:
                response += "**Sources:**\n"
                for source in sources[:3]:
                    response += f"- {source}\n"
                response += "\n"
            
            response += f"""If you have any further questions or need additional assistance, please don't hesitate to contact us.

Best regards,
{self.sender_name}
Customer Support Team
TechCorp Solutions

📧 support@techcorp.com
📞 +1 (555) 123-4567
"""
            return response
            
        except Exception as e:
            logger.error(f"Error generating KB response: {e}")
            return f"""Hi,

Thank you for reaching out. We've received your inquiry and will respond shortly.

Best regards,
{self.sender_name}"""

    def _send_auto_response_email(self, to_email: str, subject: str, response_body: str, kb_result: Dict) -> bool:
        """Send auto-response email directly (no approval needed)"""
        try:
            import json
            import subprocess
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Write email data to temp file
            temp_file = Path(__file__).parent.parent / ".email_temp.json"
            email_data = {
                "to": to_email,
                "subject": f"Re: {subject}",
                "body": response_body
            }
            temp_file.write_text(json.dumps(email_data, ensure_ascii=False), encoding='utf-8')
            
            # Run send_email.js
            result = subprocess.run(
                ['node', 'send_email.js', '--from-file', str(temp_file)],
                capture_output=True,
                text=True,
                encoding='utf-8',
                cwd=str(Path(__file__).parent.parent)
            )
            
            # Clean up temp file
            try:
                temp_file.unlink()
            except:
                pass
            
            if result.returncode == 0:
                logger.info(f"✅ Auto-response email sent successfully to {to_email}")
                
                # Create log file
                log_content = f"""---
type: auto_response_log
to: {to_email}
subject: Re: {subject}
timestamp: {datetime.now().isoformat()}
confidence: {kb_result['confidence']}
sources: {', '.join(kb_result.get('sources', []))}
---

# Auto-Response Email Log

## Email Details
- **To:** {to_email}
- **Subject:** Re: {subject}
- **Sent:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Confidence:** {kb_result['confidence']}

## Response Sent

{response_body}

---
*Sent automatically by AI Employee Vault Knowledge Base*
"""
                log_file = self.done_folder / f"AUTO_RESPONSE_{timestamp}.md"
                log_file.write_text(log_content, encoding='utf-8')
                
                return True
            else:
                logger.error(f"❌ Auto-response failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending auto-response: {e}")
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

    def _process_facebook_task(self, file_path: Path, task_content: str) -> bool:
        """Process Facebook task - Create approval file with Claude-generated content, diagrams and image support"""
        try:
            import re
            from datetime import datetime
            import subprocess
            from engine.diagram_generator import DiagramGenerator

            # Extract image_path from YAML frontmatter (if uploaded from dashboard)
            image_path = None
            if 'image_path:' in task_content:
                image_match = re.search(r'image_path:\s*(.+)', task_content)
                if image_match:
                    image_path = image_match.group(1).strip()
                    logger.info(f"📷 Found uploaded image: {image_path}")

            # Extract content
            content_match = re.search(r'## Content\s*\n\n(.+?)(?=\n##|\Z)', task_content, re.DOTALL)
            if not content_match:
                logger.warning("No content found in Facebook task")
                return False

            user_prompt = content_match.group(1).strip()

            # Check if this is a DELETE action
            is_delete = 'delete' in user_prompt.lower() and 'post id' in user_prompt.lower()

            # Extract post ID for delete actions
            post_id = ""
            if is_delete:
                post_id_match = re.search(r'ID:\s*([a-zA-Z0-9_]+)', user_prompt, re.IGNORECASE)
                if post_id_match:
                    post_id = post_id_match.group(1)
                # Create DELETE approval file
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                approval_filename = f"APPROVAL_facebook_delete_{timestamp}.md"
                approval_path = self.pending_approval_folder / approval_filename

                approval_content = f"""---
type: facebook_approval
action: facebook_delete
post_id: {post_id}
---

# Facebook Post Deletion Approval

## Action
Delete Facebook Post

## Post ID to Delete
{post_id}

## Message
Delete Facebook post ID: {post_id}

## Original Request
{user_prompt}

---

## Instructions
1. Review the post ID above
2. Move to Approved/ to delete
3. Move to Rejected/ to cancel

---
*Requires human approval before deletion*
"""
            else:
                # Detect if user wants a diagram
                diagram_keywords = ['diagram', 'flowchart', 'workflow', 'architecture', 'process', 'pipeline', 'graph', 'funnel', 'explain', 'how it works']
                needs_diagram = any(keyword in user_prompt.lower() for keyword in diagram_keywords)
                
                # Use Claude to generate professional Facebook post WITH DIAGRAM SUPPORT
                logger.info(f"🤖 Generating Facebook post with Claude...")

                if needs_diagram:
                    claude_prompt = f"""
You are a professional social media manager and expert teacher for a business company.

Generate a HIGHLY PROFESSIONAL Facebook post based on this request:
"{user_prompt}"

CRITICAL REQUIREMENTS:
1. Write in ENGLISH ONLY (no other languages)
2. Professional and engaging tone
3. Make it shareable and valuable
4. Include emojis if appropriate (max 3)
5. Focus on business value
6. Keep it under 500 characters
7. Include strong call-to-action
8. Generate 8-10 RELEVANT HASHTAGS for SEO
9. If explaining a concept, be detailed like an experienced teacher

Also generate a DETAILED Mermaid diagram code if the topic is technical (architecture, workflow, process, funnel, automation, etc.)
The diagram should be PROFESSIONAL and EDUCATIONAL with:
- Clear flow from start to end
- Proper labels for each step
- Emojis in labels for visual appeal
- Color styling for different components
- Detailed enough to explain the concept fully

Output format:
TEXT:
[your professional post here with hashtags]

MERMAID:
[mermaid code here or "NONE" if not needed]
"""
                else:
                    claude_prompt = f"""
You are a professional social media manager for a business company.

Generate a HIGHLY PROFESSIONAL Facebook post based on this request:
"{user_prompt}"

CRITICAL REQUIREMENTS:
1. Write in ENGLISH ONLY (no other languages)
2. Professional and engaging tone
3. Make it shareable and valuable
4. Include emojis if appropriate (max 3)
5. Focus on business value
6. Keep it under 500 characters
7. Include strong call-to-action
8. Generate 8-10 RELEVANT HASHTAGS for SEO

Output ONLY the Facebook post text, nothing else.
"""

                try:
                    claude_path = r"C:\Users\H P\AppData\Roaming\npm\claude.cmd"

                    # Run claude with prompt via stdin - FORCE UTF-8 ENCODING
                    result = subprocess.run(
                        [claude_path, '-p'],
                        input=claude_prompt,
                        capture_output=True,
                        text=True,
                        timeout=120,
                        shell=True,
                        encoding='utf-8',  # Force UTF-8 encoding
                        errors='replace'   # Replace invalid characters
                    )

                    generated_post = user_prompt  # Default to original prompt
                    mermaid_code = None
                    
                    if result.stdout and len(result.stdout.strip()) >= 10:
                        output = result.stdout.strip()
                        
                        # Parse output for TEXT and MERMAID sections
                        if needs_diagram and 'TEXT:' in output and 'MERMAID:' in output:
                            # Extract sections
                            text_match = re.search(r'TEXT:\s*(.+?)\n\n?MERMAID:', output, re.DOTALL)
                            mermaid_match = re.search(r'MERMAID:\s*(.+?)$', output, re.DOTALL)
                            
                            if text_match:
                                generated_post = text_match.group(1).strip()
                            if mermaid_match:
                                mermaid_raw = mermaid_match.group(1).strip()
                                if mermaid_raw.upper() != 'NONE':
                                    mermaid_code = mermaid_raw
                        else:
                            generated_post = output
                        
                        logger.info(f"✅ Facebook post generated: {generated_post[:50]}...")
                    else:
                        logger.warning(f"Claude returned empty, using original prompt")
                        if result.stderr:
                            logger.error(f"Claude error output: {result.stderr[:200]}")

                except Exception as e:
                    logger.warning(f"Claude Facebook post generation failed: {e}, using original prompt")

                # Generate diagram if Mermaid code provided
                diagram_path = None
                if mermaid_code:
                    logger.info(f"🎨 Generating diagram from Mermaid code...")
                    diagram_gen = DiagramGenerator()
                    diagram_path = diagram_gen.generate_png(mermaid_code)
                    if diagram_path:
                        logger.info(f"✅ Diagram generated: {diagram_path}")
                    else:
                        logger.warning(f"⚠️ Diagram generation failed")

                # Create POST approval file - FORCE UTF-8 ENCODING
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                approval_filename = f"APPROVAL_facebook_post_{timestamp}.md"
                approval_path = self.pending_approval_folder / approval_filename

                # Build approval content based on what we have
                if image_path or diagram_path:
                    # Has image (uploaded or generated)
                    approval_content = f"""---
type: facebook_approval
action: facebook_post
"""
                    if image_path:
                        approval_content += f"image_path: {image_path}\n"
                    if diagram_path:
                        approval_content += f"diagram_path: {diagram_path}\n"
                    
                    approval_content += f"""---

# Facebook Post Approval

## Original Request

{user_prompt}

## AI-Generated Content

{generated_post}

"""
                    if image_path:
                        approval_content += f"""
## Uploaded Image

Image file: `{image_path}`

*This image will be attached when posting*

"""
                    if diagram_path:
                        approval_content += f"""
## AI-Generated Diagram

Image file: `{diagram_path}`

*This diagram will be attached when posting*

"""
                    if mermaid_code:
                        approval_content += f"""
## Mermaid Code

```mermaid
{mermaid_code}
```

"""
                    
                    approval_content += f"""
---

## Instructions
1. Review the AI-generated post above
2. Edit if needed
3. Approve: Move to `Approved/` folder (posts to Facebook with image)
4. Reject: Move to `Rejected/` folder

---
*Generated by AI Employee Vault*
*{'Diagram included ✅' if diagram_path else 'Text only'}*
"""
                else:
                    # No image - text only
                    approval_content = f"""---
type: facebook_approval
action: facebook_post
---

# Facebook Post Approval

## Original Request

{user_prompt}

## AI-Generated Content

{generated_post}

---

## Instructions
1. Review the AI-generated post above
2. Edit if needed
3. Approve: Move to `Approved/` folder (posts to Facebook)
4. Reject: Move to `Rejected/` folder

---
*Generated by AI Employee Vault*
"""

                # Write approval file WITH UTF-8 ENCODING
                approval_path.write_text(approval_content, encoding='utf-8')
                logger.info(f"Created Facebook approval file: {approval_filename}")

                # Move original task to Done
                done_path = self.done_folder / file_path.name
                shutil.move(str(file_path), str(done_path))
                logger.info(f"Moved to Done: {file_path.name}")

                return True

        except Exception as e:
            logger.error(f"Error processing Facebook task: {e}")
            return False       
            

    def _process_facebook_comment_task(self, file_path: Path, task_content: str) -> bool:
        """Process Facebook comment task - Create approval files automatically"""
        try:
            import re
            from datetime import datetime

            logger.info(f"📘 Processing Facebook comment: {file_path.name}")

            # Extract data from content
            comment_match = re.search(r'## Comment Content\s*\n\n(.+?)(?=\n##|\Z)', task_content, re.DOTALL)
            if not comment_match:
                logger.warning(f"No comment content in {file_path.name}")
                return False

            comment_text = comment_match.group(1).strip()

            # Extract metadata
            user_name_match = re.search(r'\*\*Posted By:\*\*\s*(.+)', task_content)
            user_name = user_name_match.group(1).strip() if user_name_match else 'Unknown'

            lead_score_match = re.search(r'lead_score:\s*(\d+)', task_content)
            lead_score = int(lead_score_match.group(1)) if lead_score_match else 50

            comment_id_match = re.search(r'comment_id:\s*(.+)', task_content)
            comment_id = comment_id_match.group(1).strip() if comment_id_match else ''

            # Generate AI response using Claude Code
            ai_response = self._generate_facebook_response(comment_text)

            # Create approval files (following standard workflow)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 1. Odoo Lead Approval
            self._create_facebook_odoo_approval(
                user_name, comment_text, ai_response, lead_score, timestamp
            )

            # 2. Email Notification Approval
            self._create_facebook_email_approval(
                user_name, comment_text, ai_response, lead_score, timestamp
            )

            # 3. WhatsApp Approval (HOT leads only)
            if lead_score >= 80:
                self._create_facebook_whatsapp_approval(
                    user_name, comment_text, lead_score, timestamp
                )

            # 4. Facebook Reply Approval
            self._create_facebook_reply_approval(
                comment_id, ai_response, lead_score, timestamp
            )

            # Move original to Done
            done_path = self.done_folder / file_path.name
            shutil.move(str(file_path), str(done_path))

            logger.info(f"✅ Facebook comment processed: {file_path.name}")
            return True

        except Exception as e:
            logger.error(f"❌ Error processing Facebook comment: {e}")
            return False

    def _process_twitter_task(self, file_path: Path, task_content: str) -> bool:
        """Process Twitter task - Generate tweet with Claude and diagram (or use original prompt), then create approval file"""
        try:
            import re
            from datetime import datetime
            import subprocess
            from engine.diagram_generator import DiagramGenerator

            logger.info(f"🐦 Processing Twitter task: {file_path.name}")

            # Extract the prompt/request from content
            # Try multiple patterns to find the tweet content
            user_prompt = ""

            # Pattern 1: Look for ## Content section
            content_match = re.search(r'## Content\s*\n\n(.+?)(?=\n##|\Z)', task_content, re.DOTALL)
            if content_match:
                user_prompt = content_match.group(1).strip()
            else:
                # Pattern 2: Look for content after YAML frontmatter
                if '---' in task_content:
                    parts = task_content.split('---', 2)
                    if len(parts) >= 3:
                        # Get content after YAML frontmatter
                        content_after_yaml = parts[2].strip()
                        # Remove any markdown headers
                        user_prompt = re.sub(r'^#+\s*', '', content_after_yaml).strip()
                        # Look for the actual message content
                        if '##' in user_prompt:
                            user_prompt = user_prompt.split('##')[0].strip()

            # If still no content, use the whole content minus YAML
            if not user_prompt:
                # Remove YAML frontmatter
                if task_content.startswith('---'):
                    parts = task_content.split('---', 2)
                    if len(parts) >= 3:
                        user_prompt = parts[2].strip()
                else:
                    user_prompt = task_content.strip()

                # Clean up markdown
                user_prompt = re.sub(r'^#+\s*[^\n]*\n', '', user_prompt).strip()
                user_prompt = re.sub(r'\*\*[^*]+\*\*:\s*[^\n]*\n', '', user_prompt).strip()

            if not user_prompt:
                logger.warning(f"No content in {file_path.name}")
                logger.debug(f"File content: {task_content[:500]}")
                return False

            logger.info(f"📝 Extracted prompt: {user_prompt[:50]}...")

            # Try to use Claude to generate professional tweet WITH DIAGRAM SUPPORT
            logger.info(f"🤖 Generating tweet with Claude...")
            
            # Detect if user wants a diagram
            diagram_keywords = ['diagram', 'flowchart', 'workflow', 'architecture', 'process', 'pipeline', 'graph']
            needs_diagram = any(keyword in user_prompt.lower() for keyword in diagram_keywords)
            
            if needs_diagram:
                claude_prompt = f"""
You are a professional social media manager for an AI automation company.

Generate a Twitter post based on this request:
"{user_prompt}"

Requirements:
- Maximum 280 characters (Twitter limit)
- Include 2-3 relevant hashtags
- Make it engaging and shareable
- Include emojis if appropriate (max 2)
- Focus on value for the audience
- Professional but friendly tone

Also generate a Mermaid diagram code if the topic is technical (architecture, workflow, process, etc.)

Output format:
TEXT:
[your tweet here]

MERMAID:
[mermaid code here or "NONE" if not needed]
"""
            else:
                claude_prompt = f"""
You are a professional social media manager for an AI automation company.

Generate a Twitter post based on this request:
"{user_prompt}"

Requirements:
- Maximum 280 characters (Twitter limit)
- Include 2-3 relevant hashtags
- Make it engaging and shareable
- Include emojis if appropriate (max 2)
- Focus on value for the audience
- Professional but friendly tone

Output ONLY the tweet text, nothing else.
"""
            
            generated_tweet = user_prompt  # Default to original prompt
            mermaid_code = None
            
            try:
                claude_path = r"C:\Users\H P\AppData\Roaming\npm\claude.cmd"
                
                # Run claude with prompt via stdin
                result = subprocess.run(
                    [claude_path, '-p'],
                    input=claude_prompt,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    shell=True
                )
                
                if result.stdout and len(result.stdout.strip()) >= 10:
                    output = result.stdout.strip()
                    
                    # Parse output for TEXT and MERMAID sections
                    if 'TEXT:' in output and 'MERMAID:' in output:
                        # Extract sections
                        text_match = re.search(r'TEXT:\s*(.+?)\n\n?MERMAID:', output, re.DOTALL)
                        mermaid_match = re.search(r'MERMAID:\s*(.+?)$', output, re.DOTALL)
                        
                        if text_match:
                            generated_tweet = text_match.group(1).strip()
                        if mermaid_match:
                            mermaid_raw = mermaid_match.group(1).strip()
                            if mermaid_raw.upper() != 'NONE':
                                mermaid_code = mermaid_raw
                    else:
                        generated_tweet = output
                    
                    logger.info(f"✅ Tweet generated by Claude: {generated_tweet[:50]}...")
                    
                    # Ensure it fits Twitter limit
                    if len(generated_tweet) > 280:
                        generated_tweet = generated_tweet[:277] + "..."
                
                # Generate diagram if Mermaid code provided
                diagram_path = None
                if mermaid_code:
                    logger.info(f"🎨 Generating diagram from Mermaid code...")
                    diagram_gen = DiagramGenerator()
                    diagram_path = diagram_gen.generate_png(mermaid_code)
                    if diagram_path:
                        logger.info(f"✅ Diagram generated: {diagram_path}")
                    else:
                        logger.warning(f"⚠️ Diagram generation failed")
                
            except FileNotFoundError:
                logger.warning(f"Claude CLI not found, using original prompt")
            except Exception as e:
                logger.warning(f"Claude generation failed: {e}, using original prompt")

            # Check if thread
            is_thread = 'thread' in file_path.name.lower() or 'thread' in task_content.lower()

            # Create approval file with generated tweet
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            if is_thread:
                approval_filename = f"APPROVAL_twitter_thread_{timestamp}.md"
            else:
                approval_filename = f"APPROVAL_twitter_post_{timestamp}.md"

            approval_path = self.pending_approval_folder / approval_filename

            approval_content = f"""---
type: twitter_approval
action: twitter_{'thread' if is_thread else 'post'}
---

# Twitter {'Thread' if is_thread else 'Post'} Approval

## Original Request

{user_prompt}

## AI-Generated Content

{generated_tweet}

"""
            
            # Add diagram info if generated
            if mermaid_code:
                approval_content += f"""
## AI-Generated Diagram

Diagram generated from Mermaid code:

```mermaid
{mermaid_code}
```

"""
            
            if diagram_path:
                approval_content += f"""
## Diagram Image

Image file: `{diagram_path}`

*This image will be attached when posting*

"""

            approval_content += f"""---

## Instructions
1. Review the {'thread' if is_thread else 'post'} above
2. Edit if needed
3. Approve: Move to `Approved/` folder (opens Twitter for posting)
4. Reject: Move to `Rejected/` folder

---
*Generated by AI Employee Vault*
*{'Diagram included ✅' if diagram_path else 'Text only'}*
"""

            approval_path.write_text(approval_content, encoding='utf-8')
            logger.info(f"✅ Twitter approval created: {approval_filename}")

            # Move original to Done
            done_path = self.done_folder / file_path.name
            shutil.move(str(file_path), str(done_path))
            logger.info(f"Moved to Done: {file_path.name}")

            return True

        except Exception as e:
            logger.error(f"❌ Error processing Twitter task: {e}")
            return False
    
    def _generate_facebook_response(self, comment_text: str) -> str:
        """Generate AI response for Facebook comment using Claude Code"""
        try:
            import subprocess
            
            prompt = f"""
            You are a professional AI automation expert and full-stack developer.
            
            Someone commented on our Facebook page:
            "{comment_text}"
            
            Generate a professional, helpful response that:
            1. Acknowledges their specific interest/need
            2. Briefly mentions our expertise in AI automation and web development (2 sentences max)
            3. Includes our portfolio link: https://your-portfolio.com
            4. Invites them to send a message for more details
            5. Tone: Friendly and professional
            6. Keep it under 150 characters
            
            Do NOT use hashtags or emojis.
            """
            
            claude_path = r"C:\Users\H P\AppData\Roaming\npm\claude.cmd"
            
            # Run claude with prompt via stdin
            result = subprocess.run(
                [claude_path, '-p'],
                input=prompt,
                capture_output=True,
                text=True,
                timeout=120,
                shell=True
            )
            
            response = result.stdout.strip()
            
            if not response:
                response = "Thanks for your interest! Please send us a message for more details."
            
            return response
        
        except Exception as e:
            logger.error(f"❌ AI response error: {e}")
            return "Thanks for your interest! Please send us a message for more details."
    
    def _create_facebook_odoo_approval(self, user_name, comment_text, ai_response, lead_score, timestamp):
        """Create Odoo lead approval file"""
        approval_file = self.pending_approval_folder / f"ODOO_LEAD_facebook_{user_name.replace(' ', '_')}_{timestamp}.md"
        
        approval_content = f"""---
type: odoo_lead_approval
action: create_lead
lead_name: Facebook Lead - {user_name}
email: 
phone: 
source: Facebook Page Comment
---

# Odoo Lead Creation Approval

## Lead Details

**Name:** Facebook Lead - {user_name}
**Email:** (To be collected)
**Phone:** (To be collected)
**Source:** Facebook Page Comment
**Lead Score:** {lead_score}/100

## Original Comment

{comment_text}

## AI-Generated Response

{ai_response}

---

## Instructions
1. **Review** the lead details above
2. **Edit** if needed (add email/phone when available)
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder
"""
        
        approval_file.write_text(approval_content, encoding='utf-8')
        logger.info(f"✅ Odoo approval created: {approval_file.name}")
    
    def _create_facebook_email_approval(self, user_name, comment_text, ai_response, lead_score, timestamp):
        """Create email notification approval file"""
        approval_file = self.pending_approval_folder / f"APPROVAL_send_email_facebook_{timestamp}.md"
        
        email_body = f"""NEW FACEBOOK LEAD!

─────────────────────────────
LEAD DETAILS
─────────────────────────────
Name: {user_name}
Source: Facebook Page Comment
Lead Score: {lead_score}/100

─────────────────────────────
COMMENT
─────────────────────────────
{comment_text}

─────────────────────────────
AI-GENERATED RESPONSE
─────────────────────────────
{ai_response}

─────────────────────────────
ACTION REQUIRED
─────────────────────────────
1. Lead saved to Odoo CRM (separate approval)
2. Send personalized follow-up email
3. Respond within 1 hour for best conversion

---
AI Employee Vault
Lead Detection System
"""
        
        approval_content = f"""---
type: email_approval
action: send_email
to: bashartc14@gmail.com
subject: 🎯 New Facebook Lead - {user_name} (Score: {lead_score}/100)
---

# Email Notification Approval

## Email Body

{email_body.strip()}

---

## Instructions
1. **Review** the notification email above
2. **Edit** recipient email if needed
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder
"""
        
        approval_file.write_text(approval_content, encoding='utf-8')
        logger.info(f"✅ Email approval created: {approval_file.name}")
    
    def _create_facebook_whatsapp_approval(self, user_name, comment_text, lead_score, timestamp):
        """Create WhatsApp notification approval file (HOT leads only)"""
        approval_file = self.pending_approval_folder / f"APPROVAL_send_whatsapp_facebook_{timestamp}.md"
        
        whatsapp_message = f"""🎯 HOT FACEBOOK LEAD!

Name: {user_name}
Comment: {comment_text[:100]}...

Lead Score: {lead_score}/100

Respond within 1 hour!
"""
        
        approval_content = f"""---
type: whatsapp_approval
action: send_whatsapp
phone: +1234567890
---

# WhatsApp Hot Lead Alert

## Message

{whatsapp_message.strip()}

---

## Instructions
1. **Review** the WhatsApp alert above
2. **Edit** phone number if needed
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder
"""
        
        approval_file.write_text(approval_content, encoding='utf-8')
        logger.info(f"✅ WhatsApp approval created: {approval_file.name}")
    
    def _create_facebook_reply_approval(self, comment_id, ai_response, lead_score, timestamp):
        """Create Facebook reply approval file"""
        approval_file = self.pending_approval_folder / f"APPROVAL_facebook_reply_{timestamp}.md"
        
        approval_content = f"""---
type: facebook_approval
action: facebook_reply
comment_id: {comment_id}
lead_score: {lead_score}
---

# Facebook Comment Reply Approval

## Comment ID to Reply

{comment_id}

## AI-Generated Response

{ai_response}

## Lead Score

{lead_score}/100

---

## Instructions
1. **Review** the AI-generated response above
2. **Edit** if needed
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder
"""
        
        approval_file.write_text(approval_content, encoding='utf-8')
        logger.info(f"✅ Facebook reply approval created: {approval_file.name}")

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

        # FIRST check for HR Applications (NEW - HIGH PRIORITY)
        if filename.startswith('HR_APPLICATION') or 'type: hr_application' in content_lower:
            return 'hr_application'

        # FIRST check for Customer Support emails (NEW - HIGH PRIORITY)
        support_keywords = ['support', 'ticket', 'urgent', 'customer support',
                           'help needed', 'issue', 'problem', 'complaint']
        if any(keyword in content_lower for keyword in support_keywords):
            # Check if it looks like a support request
            if any(word in content_lower for word in ['urgent', 'issue', 'problem', 'help', 'support']):
                return 'support_ticket'

        # FIRST check for Twitter tasks (MUST be before other social media and inbox)
        # Check both filename starting with 'tweet' or 'twitter', and YAML frontmatter
        if (filename_lower.startswith('tweet') or
            filename_lower.startswith('twitter') or
            'type: twitter' in content_lower or
            'action: twitter' in content_lower):
            return 'twitter'

        # FIRST check for Facebook comment tasks (NEW - must be before general Facebook)
        if filename.startswith('FACEBOOK_COMMENT') or 'type: facebook_comment' in content_lower:
            return 'facebook_comment'

        # First check for Facebook tasks (NEW - must be before Odoo)
        if 'facebook' in filename_lower or 'facebook' in content_lower:
            return 'facebook'

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

        # Check for direct email/whatsapp/linkedin tasks (with YAML frontmatter) - BEFORE inbox detection
        if 'email' in filename_lower or 'type: email' in content_lower:
            return 'email'
        elif 'whatsapp' in filename_lower or 'type: whatsapp' in content_lower:
            return 'whatsapp'
        elif 'linkedin' in filename_lower or 'type: linkedin' in content_lower:
            return 'linkedin'

        if 'send email' in content_lower or 'send whatsapp' in content_lower:
          return 'inbox_email'

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

        # Check for Facebook with YAML frontmatter
        if 'facebook' in filename_lower or 'type: facebook' in content_lower:
            return 'facebook'
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
