"""
Gmail Watcher - Silver Tier Implementation
Monitors Gmail for important unread emails and creates tasks
Now with intelligent filtering to reduce noise!
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from pathlib import Path
from datetime import datetime
import time
import pickle
import os

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
    PROFESSIONAL_KEYWORDS = ['meeting', 'project', 'urgent']
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
    'https://www.googleapis.com/auth/gmail.send'
]
VAULT = Path(__file__).parent
NEEDS_ACTION = VAULT / "Needs Action"
TOKEN_FILE = VAULT / "token.pickle"
CREDENTIALS_FILE = VAULT / "credentials.json"

# Ensure folder exists
NEEDS_ACTION.mkdir(exist_ok=True)

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

    def create_task_from_email(self, message_data):
        """Create task file from email"""
        try:
            message_id = message_data['id']
            reason = message_data.get('reason', 'Important email')
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

        except Exception as e:
            print(f"❌ Error creating task from email: {e}")

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
                time.sleep(120)

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
                time.sleep(120)

if __name__ == "__main__":
    watcher = GmailWatcher()
    if watcher.authenticate():
        watcher.run()
    else:
        print("\n❌ Authentication failed. Please set up credentials.json")
