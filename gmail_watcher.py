"""
Gmail Watcher - Customer Support AI & HR Hiring Automation Integration
Monitors Gmail for support emails and job applications with resume attachments

Now integrates with:
- Customer Support AI (ticket creation, auto-response)
- HR Hiring Automation (resume parsing, candidate scoring, interview scheduling)
- Smart filtering (promotions, spam, social media)
- Attachment extraction (PDF resumes)
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from pathlib import Path
from datetime import datetime
import time
import pickle
import os
import base64
import io

# Import filtering configuration
try:
    from gmail_filter_config import (
        MIN_IMPORTANCE_SCORE, PROMO_KEYWORDS, WHITELIST_DOMAINS,
        BLACKLIST_DOMAINS, PROFESSIONAL_KEYWORDS, SPAM_INDICATORS,
        ENABLE_CATEGORY_FILTER, ENABLE_KEYWORD_FILTER, ENABLE_WHITELIST,
        ENABLE_BLACKLIST, ENABLE_IMPORTANCE_MARKER, ENABLE_PROFESSIONAL_BOOST,
        ENABLE_SPAM_DETECTION, VERBOSE_FILTERING
    )
except ImportError:
    # Fallback to defaults if config file not found
    print("⚠️  gmail_filter_config.py not found, using default settings")
    MIN_IMPORTANCE_SCORE = 5
    PROMO_KEYWORDS = ['unsubscribe', 'discount', 'sale', 'offer']
    WHITELIST_DOMAINS = []
    BLACKLIST_DOMAINS = ['noreply@', 'no-reply@']
    PROFESSIONAL_KEYWORDS = ['meeting', 'project', 'urgent', 'resume', 'application', 'job', 'career', 'position']
    SPAM_INDICATORS = ['congratulations', 'winner', 'prize']
    ENABLE_CATEGORY_FILTER = True
    ENABLE_KEYWORD_FILTER = True
    ENABLE_WHITELIST = True
    ENABLE_BLACKLIST = True
    ENABLE_IMPORTANCE_MARKER = True
    ENABLE_PROFESSIONAL_BOOST = True
    ENABLE_SPAM_DETECTION = True
    VERBOSE_FILTERING = True

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.modify'
]
VAULT = Path(__file__).parent
NEEDS_ACTION = VAULT / "Needs Action"
RESUMES_FOLDER = VAULT / "Resumes"
TOKEN_FILE = VAULT / "token.pickle"
CREDENTIALS_FILE = VAULT / "credentials.json"

# Ensure folders exist
NEEDS_ACTION.mkdir(exist_ok=True)
RESUMES_FOLDER.mkdir(exist_ok=True)

class GmailWatcher:
    def __init__(self):
        self.service = None
        self.processed_ids = set()
        self.filtered_count = 0
        self.processed_count = 0

    def is_important_email(self, message):
        """
        Determine if email is important enough for Needs Action
        Returns: (bool, reason, score)
        """
        try:
            # Get full message details
            msg = self.service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()

            # Extract headers
            headers = {h['name']: h['value']
                      for h in msg['payload']['headers']}

            subject = headers.get('Subject', '').lower()
            sender = headers.get('From', '').lower()
            labels = msg.get('labelIds', [])

            importance_score = 5  # Start with neutral score

            # ========== FILTER 1: Gmail Categories (Most Reliable) ==========

            # Block promotional emails
            if 'CATEGORY_PROMOTIONS' in labels:
                return False, "Promotional email (Gmail category)", 0

            # Block social media notifications
            if 'CATEGORY_SOCIAL' in labels:
                return False, "Social media notification", 0

            # Block updates/receipts
            if 'CATEGORY_UPDATES' in labels:
                return False, "Update/receipt email", 0

            # Block forum/mailing list emails
            if 'CATEGORY_FORUMS' in labels:
                return False, "Forum/mailing list", 0

            # Boost primary category emails
            if 'CATEGORY_PRIMARY' in labels:
                importance_score += 3

            # ========== FILTER 2: Gmail Importance Marker ==========

            if 'IMPORTANT' in labels:
                importance_score += 3

            # ========== FILTER 3: Sender Blacklist ==========

            for blocked_domain in BLACKLIST_DOMAINS:
                if blocked_domain in sender:
                    return False, f"Blacklisted sender ({blocked_domain})", 0

            # ========== FILTER 4: Sender Whitelist ==========

            for allowed_domain in WHITELIST_DOMAINS:
                if allowed_domain in sender:
                    return True, f"Whitelisted sender ({allowed_domain})", 10

            # ========== FILTER 5: Promotional Keywords ==========

            promo_count = sum(1 for keyword in PROMO_KEYWORDS if keyword in subject)
            if promo_count >= 2:
                return False, f"Promotional keywords detected ({promo_count} matches)", 0
            elif promo_count == 1:
                importance_score -= 2

            # ========== FILTER 6: Professional Indicators ==========

            # Check for professional keywords
            professional_keywords = ['meeting', 'project', 'deadline', 'urgent',
                                    'invoice', 'contract', 'proposal', 'review',
                                    'approval', 'request', 'inquiry', 'question']

            professional_count = sum(1 for keyword in professional_keywords if keyword in subject)
            if professional_count > 0:
                importance_score += professional_count

            # ========== FILTER 7: Spam Indicators ==========

            spam_indicators = ['congratulations', 'winner', 'claim', 'prize',
                              'verify your account', 'suspended', 'unusual activity']

            if any(indicator in subject for indicator in spam_indicators):
                importance_score -= 3

            # ========== FINAL DECISION ==========

            if importance_score >= MIN_IMPORTANCE_SCORE:
                return True, f"Important email (score: {importance_score})", importance_score
            else:
                return False, f"Low importance (score: {importance_score})", importance_score

        except Exception as e:
            print(f"⚠️  Error filtering email: {e}")
            # On error, allow email through (fail-safe)
            return True, "Error during filtering (allowed by default)", 5

    def authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        # Load existing token
        if TOKEN_FILE.exists():
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)

        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not CREDENTIALS_FILE.exists():
                    print("❌ credentials.json not found!")
                    print("Please download from Google Cloud Console")
                    return False

                flow = InstalledAppFlow.from_client_secrets_file(
                    str(CREDENTIALS_FILE), SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
            
            # Also save as JSON for Node.js send_email.js
            import json
            json_token = {
                'token': creds.token,
                'refresh_token': creds.refresh_token,
                'token_uri': creds.token_uri,
                'client_id': creds.client_id,
                'client_secret': creds.client_secret,
                'scopes': creds.scopes
            }
            with open(VAULT / 'gmail_token.json', 'w', encoding='utf-8') as json_file:
                json.dump(json_token, json_file, indent=2)
            
            print("✓ Token saved (pickle + JSON)")

        self.service = build('gmail', 'v1', credentials=creds)
        print("✓ Gmail authenticated successfully")
        return True

    def check_for_new_emails(self):
        """Check for unread emails and filter for importance"""
        try:
            # Query: unread emails
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()

            messages = results.get('messages', [])
            new_messages = [m for m in messages if m['id'] not in self.processed_ids]

            # Filter for important emails only
            important_messages = []
            for msg in new_messages:
                is_important, reason, score = self.is_important_email(msg)

                if is_important:
                    important_messages.append({
                        'id': msg['id'],
                        'reason': reason,
                        'score': score
                    })
                    print(f"  ✓ Important: {reason}")
                else:
                    self.filtered_count += 1
                    print(f"  ✗ Filtered: {reason}")
                    # Mark as processed so we don't check again
                    self.processed_ids.add(msg['id'])

            return important_messages
        except Exception as e:
            print(f"❌ Error checking Gmail: {e}")
            return []

    def extract_attachments(self, message_data):
        """
        Extract attachments from email (PDF, Word, Text files)
        Returns: List of saved file paths
        """
        try:
            message_id = message_data['id']
            saved_files = []

            # Get full email with attachments
            msg = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            # Extract headers for context
            headers = {h['name']: h['value']
                      for h in msg['payload']['headers']}
            subject = headers.get('Subject', 'No Subject')
            from_email = headers.get('From', 'Unknown')

            # Check if email has attachments
            if 'parts' not in msg['payload']:
                return saved_files

            # Iterate through parts to find attachments
            for part in msg['payload']['parts']:
                if part['filename'] and 'attachmentId' in part['body']:
                    filename = part['filename']
                    attachment_id = part['body']['attachmentId']
                    mime_type = part.get('mimeType', '')

                    # Check if it's a resume file (PDF, Word, or Text)
                    is_resume_file = (
                        filename.lower().endswith('.pdf') or
                        filename.lower().endswith('.docx') or
                        filename.lower().endswith('.doc') or
                        filename.lower().endswith('.txt') or
                        filename.lower().endswith('.md') or
                        'resume' in filename.lower() or
                        'cv' in filename.lower() or
                        mime_type in [
                            'application/pdf',
                            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                            'application/msword',
                            'text/plain'
                        ]
                    )

                    if is_resume_file:
                        print(f"  📎 Found attachment: {filename} ({mime_type})")

                        # Get attachment data
                        attachment = self.service.users().messages().attachments().get(
                            userId='me',
                            messageId=message_id,
                            id=attachment_id
                        ).execute()

                        # Decode file data
                        file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))

                        # Create safe filename
                        safe_filename = "".join(c for c in filename if c.isalnum() or c in '._- ').strip()
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

                        # Determine file extension from filename
                        file_ext = Path(filename).suffix.lower() if Path(filename).suffix else '.bin'

                        # Save to Resumes folder
                        resume_path = RESUMES_FOLDER / f"RESUME_{timestamp}_{safe_filename}"
                        resume_path.write_bytes(file_data)

                        print(f"  ✅ Saved resume: {resume_path.name}")
                        saved_files.append(str(resume_path))

            return saved_files

        except Exception as e:
            print(f"❌ Error extracting attachments: {e}")
            return []

    def create_hr_task_from_email(self, message_data, resume_files, email_body_text=""):
        """
        Create HR-specific task file for resume emails
        Now handles both attachment resumes AND resume text in email body
        """
        try:
            message_id = message_data['id']
            reason = message_data.get('reason', 'Job application received')
            score = message_data.get('score', 5)

            # Get full email details
            msg = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            # Extract headers
            headers = {h['name']: h['value']
                      for h in msg['payload']['headers']}

            from_email = headers.get('From', 'Unknown')
            subject = headers.get('Subject', 'No Subject')
            date = headers.get('Date', '')

            # Get email body (full content, not just snippet)
            email_body = self._extract_email_body(msg)
            
            # Use provided email_body_text if available, otherwise extract from message
            if not email_body_text and email_body:
                email_body_text = email_body

            # Create HR task file - use HR_APPLICATION prefix for proper routing
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            task_filename = f"HR_APPLICATION_{message_id[:8]}.md"
            task_path = NEEDS_ACTION / task_filename
            
            # Build resume files section
            if resume_files:
                resume_section = chr(10).join([f"- `{f}`" for f in resume_files])
                resume_instruction = "Parse attached resume file(s)"
            elif email_body_text:
                resume_section = "**Resume in email body** (see Email Content section below)"
                resume_instruction = "Extract and parse resume from email body content"
            else:
                resume_section = "No resume attachments found"
                resume_instruction = "No resume found - may need manual review"

            # Create HR task file
            task_content = f'''---
type: hr_application
from: {from_email}
subject: {subject}
received: {datetime.now().isoformat()}
gmail_id: {message_id}
priority: high
importance_score: {score}
filter_reason: {reason}
status: pending_review
resume_files: {resume_files if resume_files else "[]"}
---

# Job Application Received

**From:** {from_email}
**Subject:** {subject}
**Date:** {date}
**Importance Score:** {score}/10
**Filter Reason:** {reason}

## Application Details

{email_body_text[:500] if email_body_text else 'No content in email body'}

## Resume Files

{resume_section}

## Email Content (Full)

{email_body_text[:3000] if email_body_text else 'No content'}

## Next Steps

- [ ] {resume_instruction}
- [ ] Score candidate (ATS-style evaluation)
- [ ] If score >= 80: Schedule interview
- [ ] If score 60-79: Review manually
- [ ] If score < 60: Send rejection email

## Instructions

This is a job application email.
The HR automation system will:
1. Parse the resume(s) or extract from email body
2. Extract candidate information
3. Score the candidate (0-100)
4. Log to Google Sheets
5. Create Google Doc
6. Create interview approval if score >= 80
7. Send appropriate response to candidate
'''

            # Save to Needs_Action
            task_path.write_text(task_content, encoding='utf-8')

            print(f"✓ Created HR task: {task_filename}")
            print(f"  From: {from_email}")
            print(f"  Subject: {subject[:50]}...")
            if resume_files:
                print(f"  Resumes: {len(resume_files)} file(s)")
            elif email_body_text:
                print(f"  Resume: In email body ({len(email_body_text)} chars)")
            else:
                print(f"  Resume: Not found")

            # Mark as processed
            self.processed_ids.add(message_id)
            self.processed_count += 1

            return task_path

        except Exception as e:
            print(f"❌ Error creating HR task: {e}")
            return None
    
    def _extract_email_body(self, msg):
        """Extract full email body text from Gmail message"""
        try:
            # Try to get plain text part first
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                        data = part['body']['data']
                        text = base64.urlsafe_b64decode(data).decode('utf-8')
                        return text
                    elif part['mimeType'] == 'text/html' and 'data' in part['body']:
                        data = part['body']['data']
                        html = base64.urlsafe_b64decode(data).decode('utf-8')
                        # Simple HTML to text conversion
                        text = re.sub(r'<[^>]+>', '', html)
                        return text.strip()
            elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
                data = msg['payload']['body']['data']
                text = base64.urlsafe_b64decode(data).decode('utf-8')
                return text
            
            return msg.get('snippet', '')
        except Exception as e:
            print(f"⚠️  Error extracting email body: {e}")
            return msg.get('snippet', '')

    def is_resume_email(self, message):
        """
        Check if email is a job application/resume submission
        Returns: (bool, confidence_score)
        """
        try:
            # Get message details
            msg = self.service.users().messages().get(
                userId='me',
                id=message['id'],
                format='metadata',
                metadataHeaders=['Subject', 'From']
            ).execute()

            headers = {h['name']: h['value']
                      for h in msg['payload']['headers']}
            subject = headers.get('Subject', '').lower()
            sender = headers.get('From', '').lower()

            # Keywords that indicate job application
            resume_keywords = [
                'resume', 'cv', 'curriculum vitae', 'application',
                'job application', 'career', 'position', 'hiring',
                'job opening', 'interested in', 'apply for',
                'software engineer', 'developer', 'programmer'
            ]

            # Check subject for resume keywords
            keyword_matches = sum(1 for keyword in resume_keywords if keyword in subject)

            # Check if sender domain is common job sites
            job_site_domains = ['linkedin.com', 'indeed.com', 'glassdoor.com', 'monster.com']
            is_from_job_site = any(domain in sender for domain in job_site_domains)

            # Calculate confidence
            confidence = 0
            if keyword_matches >= 2:
                confidence = 0.9  # Very confident
            elif keyword_matches == 1:
                confidence = 0.7  # Likely
            elif is_from_job_site:
                confidence = 0.6  # Possible

            return confidence >= 0.6, confidence

        except Exception as e:
            print(f"⚠️  Error checking if resume email: {e}")
            return False, 0.0

    def create_task_from_email(self, message_data):
        """Create task file from email"""
        try:
            message_id = message_data['id']
            reason = message_data.get('reason', 'Important email')
            score = message_data.get('score', 5)

            # Check if this is a resume/job application email
            is_resume, confidence = self.is_resume_email(message_data)

            if is_resume:
                print(f"  💼 Detected job application (confidence: {confidence:.0%})")

                # Extract resume attachments
                resume_files = self.extract_attachments(message_data)

                # Get full email to check for Google Docs link
                msg = self.service.users().messages().get(
                    userId='me',
                    id=message_id,
                    format='full'
                ).execute()
                
                # Extract email body
                email_body = self._extract_email_body(msg)
                
                # Check for Google Docs link in email body
                google_docs_content = None
                if email_body:
                    google_docs_content = self._fetch_google_docs_link(email_body)

                if resume_files:
                    print(f"  ✅ Extracted {len(resume_files)} resume(s)")
                    # Create HR-specific task with attachments
                    return self.create_hr_task_from_email(message_data, resume_files, email_body)
                elif google_docs_content and google_docs_content.get('success'):
                    print(f"  ✅ Fetched Google Docs resume: {google_docs_content.get('title')}")
                    # Save Google Docs content as temp file for parsing
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    temp_file = RESUMES_FOLDER / f"GOOGLE_DOCS_{timestamp}.txt"
                    temp_file.write_text(google_docs_content['content'], encoding='utf-8')
                    
                    # Create HR task with Google Docs file
                    return self.create_hr_task_from_email(message_data, [str(temp_file)], email_body)
                elif email_body:
                    print(f"  📝 No attachments, using email body ({len(email_body)} chars)")
                    # Create HR task with email body text (resume might be in body)
                    return self.create_hr_task_from_email(message_data, [], email_body)
                else:
                    print(f"  ⚠️  No resume attachments or content found")
                    # Still create HR task - may need manual review
                    return self.create_hr_task_from_email(message_data, [], "")

            # For non-resume emails, use standard task creation
            # Get full email details
            msg = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            # Extract headers
            headers = {h['name']: h['value']
                      for h in msg['payload']['headers']}

            from_email = headers.get('From', 'Unknown')
            subject = headers.get('Subject', 'No Subject')
            date = headers.get('Date', '')

            # Get email body snippet
            snippet = msg.get('snippet', '')

            # Create task file
            task_content = f'''---
type: email
from: {from_email}
subject: {subject}
received: {datetime.now().isoformat()}
gmail_id: {message_id}
priority: high
importance_score: {score}
filter_reason: {reason}
status: pending
---

# Email from {from_email}

**Subject:** {subject}
**Date:** {date}
**Importance Score:** {score}/10
**Filter Reason:** {reason}

## Email Content

{snippet}

## Suggested Actions

- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Mark as complete when done

## Instructions

Analyze this email and determine appropriate response.
If reply needed, draft it and request approval before sending.
'''

            # Save to Needs_Action
            task_file = NEEDS_ACTION / f"EMAIL_{message_id[:8]}.md"
            task_file.write_text(task_content, encoding='utf-8')

            print(f"✓ Created task: {task_file.name}")
            print(f"  From: {from_email}")
            print(f"  Subject: {subject[:50]}...")
            print(f"  Score: {score}/10")

            # Mark as processed
            self.processed_ids.add(message_id)
            self.processed_count += 1

            return task_file

        except Exception as e:
            print(f"❌ Error creating task from email: {e}")
            return None
    
    def _fetch_google_docs_link(self, email_body):
        """
        Check email body for Google Docs URL and fetch content
        
        Args:
            email_body: Email body text
        
        Returns:
            dict with content if Google Docs found and fetched, None otherwise
        """
        try:
            import re
            
            # Look for Google Docs URL pattern
            docs_pattern = r'https?://docs\.google\.com/document/d/([a-zA-Z0-9_-]+)'
            match = re.search(docs_pattern, email_body)
            
            if match:
                doc_url = match.group(0)
                print(f"  🔗 Found Google Docs URL: {doc_url}")
                
                # Fetch content using Google Docs Service
                from services.google.docs_service import GoogleDocsService
                docs_service = GoogleDocsService()
                
                result = docs_service.fetch_from_url(doc_url)
                
                if result.get('success'):
                    print(f"  ✅ Successfully fetched Google Doc: {result.get('title')}")
                    print(f"  📄 Content length: {len(result.get('content', ''))} chars")
                    return result
                else:
                    print(f"  ❌ Failed to fetch Google Doc: {result.get('error')}")
                    return None
            
            return None
            
        except Exception as e:
            print(f"  ⚠️  Error fetching Google Docs: {e}")
            return None

    def run(self):
        """Main watcher loop"""
        print("="*60)
        print("Gmail Watcher Started - With Smart Filtering")
        print("="*60)
        print(f"Vault: {VAULT}")
        print(f"Monitoring: Your Gmail inbox")
        print(f"Checking: Every 2 minutes")
        print(f"Filter: Intelligent importance detection")
        print(f"Min Score: {MIN_IMPORTANCE_SCORE}/10")
        print("\n📊 Filtering Rules:")
        print(f"  ✓ Primary inbox emails")
        print(f"  ✓ Gmail 'Important' marked emails")
        print(f"  ✓ Professional keywords detected")
        print(f"  ✗ Promotional emails (Gmail category)")
        print(f"  ✗ Social media notifications")
        print(f"  ✗ Updates/receipts")
        print(f"  ✗ Forums/mailing lists")
        print(f"  ✗ Emails with promotional keywords")
        print(f"  ✗ Blacklisted senders")
        print("\n💼 HR Features:")
        print(f"  ✓ Auto-detect job applications")
        print(f"  ✓ Extract PDF resume attachments")
        print(f"  ✓ Create HR tasks for resume parsing")
        print("\nPress Ctrl+C to stop\n")

        while True:
            try:
                new_emails = self.check_for_new_emails()

                if new_emails:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Found {len(new_emails)} important email(s)")

                    for email in new_emails:
                        self.create_task_from_email(email)

                    # Show statistics
                    total = self.processed_count + self.filtered_count
                    if total > 0:
                        filter_rate = (self.filtered_count / total) * 100
                        print(f"\n📊 Statistics:")
                        print(f"  Processed: {self.processed_count}")
                        print(f"  Filtered: {self.filtered_count}")
                        print(f"  Filter Rate: {filter_rate:.1f}%")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] No new important emails")

                # Wait 2 minutes
                time.sleep(60)

            except KeyboardInterrupt:
                print("\n\n✓ Gmail watcher stopped by user")
                print(f"\n📊 Final Statistics:")
                print(f"  Total Processed: {self.processed_count}")
                print(f"  Total Filtered: {self.filtered_count}")
                total = self.processed_count + self.filtered_count
                if total > 0:
                    filter_rate = (self.filtered_count / total) * 100
                    print(f"  Filter Rate: {filter_rate:.1f}%")
                    print(f"  Noise Reduction: {self.filtered_count} unwanted emails blocked")
                break
            except Exception as e:
                print(f"❌ Error in watcher loop: {e}")
                time.sleep(60)

if __name__ == "__main__":
    watcher = GmailWatcher()
    if watcher.authenticate():
        watcher.run()
    else:
        print("\n❌ Authentication failed. Please set up credentials.json")
