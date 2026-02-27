"""
Gmail Watcher - Silver Tier Implementation
Monitors Gmail for important unread emails and creates tasks
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
        """Check for unread important emails"""
        try:
            # Query: unread emails (removed 'is:important' for testing)
            # Change back to 'is:unread is:important' after testing
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=10
            ).execute()

            messages = results.get('messages', [])
            new_messages = [m for m in messages if m['id'] not in self.processed_ids]

            return new_messages
        except Exception as e:
            print(f"❌ Error checking Gmail: {e}")
            return []

    def create_task_from_email(self, message_id):
        """Create task file from email"""
        try:
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
status: pending
---

# Email from {from_email}

**Subject:** {subject}
**Date:** {date}

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

            # Mark as processed
            self.processed_ids.add(message_id)

        except Exception as e:
            print(f"❌ Error creating task from email: {e}")

    def run(self):
        """Main watcher loop"""
        print("="*60)
        print("Gmail Watcher Started")
        print("="*60)
        print(f"Vault: {VAULT}")
        print(f"Monitoring: Your Gmail inbox")
        print(f"Checking: Every 2 minutes")
        print(f"Filter: Unread + Important emails")
        print("\nPress Ctrl+C to stop\n")

        while True:
            try:
                new_emails = self.check_for_new_emails()

                if new_emails:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Found {len(new_emails)} new email(s)")

                    for email in new_emails:
                        self.create_task_from_email(email['id'])
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] No new emails")

                # Wait 2 minutes
                time.sleep(120)

            except KeyboardInterrupt:
                print("\n\n✓ Gmail watcher stopped by user")
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
