"""
Customer Support AI Agent - Workflow 4
Professional FTE Automation for Customer Support

Detects support emails → Categorizes by urgency → Drafts response → 
Creates ticket → Requires approval → Sends response → Logs to Google Drive

Sells for: $800-2500/month per client
"""

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from pathlib import Path
from datetime import datetime
import json
import re
import os
import sys

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
from engine.logger import logger

# Paths
VAULT = Path(__file__).parent.parent
NEEDS_ACTION = VAULT / "Needs Action"
PENDING_APPROVAL = VAULT / "Pending Approval"
APPROVED = VAULT / "Approved"
DONE = VAULT / "Done"
SUPPORT_TICKETS = VAULT / "Support_Tickets"

# Ensure folders exist
for folder in [SUPPORT_TICKETS, NEEDS_ACTION, PENDING_APPROVAL]:
    folder.mkdir(exist_ok=True)

# Support categories
SUPPORT_CATEGORIES = {
    'urgent': ['urgent', 'asap', 'emergency', 'critical', 'down', 'broken', 'not working'],
    'billing': ['invoice', 'payment', 'billing', 'refund', 'charge', 'price', 'cost'],
    'technical': ['bug', 'error', 'issue', 'problem', 'technical', 'help', 'support'],
    'feature': ['feature', 'request', 'suggestion', 'improvement', 'idea'],
    'general': ['info', 'information', 'question', 'inquiry', 'pricing']
}

# Auto-response templates
RESPONSE_TEMPLATES = {
    'urgent': """Dear {customer_name},

Thank you for contacting us regarding this urgent matter. We understand the importance of resolving this quickly.

A senior support engineer has been notified and will respond within 1 hour.

Ticket ID: {ticket_id}
Priority: URGENT
Estimated Response: Within 1 hour

Best regards,
Customer Support Team""",

    'billing': """Dear {customer_name},

Thank you for your inquiry regarding billing.

Our billing specialist will review your account and respond within 4 hours during business hours.

Ticket ID: {ticket_id}
Priority: Normal
Estimated Response: Within 4 hours

Best regards,
Billing Support Team""",

    'technical': """Dear {customer_name},

Thank you for contacting technical support.

We've received your request and a support engineer will investigate this issue.

Ticket ID: {ticket_id}
Priority: Normal
Estimated Response: Within 24 hours

Best regards,
Technical Support Team""",

    'feature': """Dear {customer_name},

Thank you for your feature suggestion! We appreciate customers like you who help us improve.

Your feedback has been forwarded to our product team for consideration.

Ticket ID: {ticket_id}
Status: Under Review

Best regards,
Product Team""",

    'general': """Dear {customer_name},

Thank you for contacting us.

We've received your inquiry and will respond as soon as possible.

Ticket ID: {ticket_id}
Priority: Normal
Estimated Response: Within 24 hours

Best regards,
Customer Support Team"""
}


class CustomerSupportAI:
    """Professional Customer Support Automation"""
    
    def __init__(self):
        self.service = None
        self.docs_service = None
        self.drive_service = None
        self.tickets_processed = 0
    
    def authenticate(self):
        """Authenticate with Google APIs"""
        try:
            # Load Gmail credentials
            from gmail_watcher import GmailWatcher
            watcher = GmailWatcher()
            if not watcher.authenticate():
                return False
            
            self.service = watcher.service
            
            # Load Google Docs/Drive services
            from services.google import GoogleDocsService, GoogleDriveService
            self.docs_service = GoogleDocsService()
            self.drive_service = GoogleDriveService()
            
            logger.info("✓ Customer Support AI authenticated")
            return True
            
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False
    
    def categorize_email(self, subject: str, body: str) -> str:
        """Categorize support email by type"""
        text = (subject + " " + body).lower()
        
        # Check each category
        for category, keywords in SUPPORT_CATEGORIES.items():
            if any(keyword in text for keyword in keywords):
                return category
        
        return 'general'
    
    def extract_customer_info(self, email_data: dict) -> dict:
        """Extract customer information from email"""
        return {
            'name': email_data.get('from_name', 'Valued Customer'),
            'email': email_data.get('from_email', ''),
            'subject': email_data.get('subject', ''),
            'ticket_id': f"SUP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        }
    
    def generate_ticket_id(self) -> str:
        """Generate unique support ticket ID"""
        return f"SUP-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def create_support_ticket(self, email_data: dict, category: str, ticket_id: str):
        """Create support ticket file and Google Doc"""
        try:
            customer = self.extract_customer_info(email_data)
            customer['ticket_id'] = ticket_id
            
            # Generate auto-response
            template = RESPONSE_TEMPLATES.get(category, RESPONSE_TEMPLATES['general'])
            auto_response = template.format(**customer)
            
            # Create ticket file
            ticket_content = f"""---
type: support_ticket
ticket_id: {ticket_id}
category: {category}
priority: {'high' if category == 'urgent' else 'normal'}
customer_email: {customer['email']}
customer_name: {customer['name']}
subject: {customer['subject']}
created: {datetime.now().isoformat()}
status: new
auto_response_sent: false
---

# Support Ticket: {ticket_id}

## Customer Information
- **Name:** {customer['name']}
- **Email:** {customer['email']}
- **Category:** {category.title()}
- **Priority:** {'High ⚠️' if category == 'urgent' else 'Normal'}

## Original Email
- **Subject:** {customer['subject']}
- **Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Content:**
{email_data.get('body', 'No content')}

## Auto-Response Sent
```
{auto_response}
```

## Action Required
- [ ] Review customer issue
- [ ] Draft detailed response (if needed)
- [ ] Resolve issue or escalate
- [ ] Mark ticket as resolved

## Notes
Add resolution notes here...
"""
            
            # Save ticket file
            ticket_file = SUPPORT_TICKETS / f"{ticket_id}.md"
            ticket_file.write_text(ticket_content, encoding='utf-8')
            
            # Create Google Doc for ticket (for record keeping)
            doc_title = f"Support Ticket {ticket_id} - {customer['name']}"
            doc_content = f"""
SUPPORT TICKET: {ticket_id}
=====================================

Customer: {customer['name']} ({customer['email']})
Category: {category.title()}
Priority: {'HIGH' if category == 'urgent' else 'Normal'}
Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

ORIGINAL ISSUE:
{email_data.get('body', 'No content')}

RESOLUTION:
[To be filled by support agent]
"""
            
            doc_result = self.docs_service.create_document(doc_title, doc_content)
            
            # Save to Support Tickets folder in Drive
            if doc_result['success']:
                folder_id = self.drive_service.get_or_create_folder("Support Tickets")
                # Move doc to folder (implementation depends on Drive service)
            
            # Create approval task for sending auto-response
            self.create_approval_task(customer, auto_response, ticket_id, category)
            
            logger.info(f"✓ Support ticket created: {ticket_id}")
            logger.info(f"  Customer: {customer['name']}")
            logger.info(f"  Category: {category}")
            logger.info(f"  Google Doc: {doc_result.get('document', {}).get('webViewLink', 'N/A')}")
            
            return {
                'success': True,
                'ticket_id': ticket_id,
                'category': category,
                'doc_link': doc_result.get('document', {}).get('webViewLink')
            }
            
        except Exception as e:
            logger.error(f"Error creating support ticket: {e}")
            return {'success': False, 'error': str(e)}
    
    def create_approval_task(self, customer: dict, response: str, ticket_id: str, category: str):
        """Create approval task for sending auto-response"""
        try:
            approval_content = f"""---
type: email_approval
action: send_email
to: {customer['email']}
subject: Re: {customer['subject']} (Ticket: {ticket_id})
ticket_id: {ticket_id}
category: {category}
---

# Email Response Approval

## Support Ticket Details
- **Ticket ID:** {ticket_id}
- **Customer:** {customer['name']} ({customer['email']})
- **Category:** {category.title()}
- **Priority:** {'High ⚠️' if category == 'urgent' else 'Normal'}

## Auto-Generated Response

## Email Body

{response}

---

## Instructions
1. **Review** the auto-generated response
2. **Edit** if needed for personalization
3. **Approve:** Move to `Approved/` folder to send
4. **Reject:** Move to `Rejected/` folder if manual response needed

## Notes
- This is an AI-generated auto-response
- For urgent tickets, consider personal follow-up
- Response will be sent automatically upon approval
"""
            
            approval_file = PENDING_APPROVAL / f"APPROVAL_support_{ticket_id}.md"
            approval_file.write_text(approval_content, encoding='utf-8')
            
            logger.info(f"✓ Approval task created: {approval_file.name}")
            
        except Exception as e:
            logger.error(f"Error creating approval task: {e}")
    
    def log_ticket_to_drive(self, ticket_data: dict):
        """Log support ticket to Google Sheets for tracking"""
        try:
            from services.google import GoogleSheetsService
            
            sheets = GoogleSheetsService()
            
            # Create or get tracking spreadsheet
            sheet_title = "Support Tickets Tracker"
            
            # Ticket data row
            ticket_row = [
                ticket_data.get('ticket_id', ''),
                ticket_data.get('customer_name', ''),
                ticket_data.get('customer_email', ''),
                ticket_data.get('category', ''),
                ticket_data.get('priority', 'Normal'),
                ticket_data.get('created', ''),
                'New',  # Status
                ticket_data.get('doc_link', '')
            ]
            
            # Append to sheet
            result = sheets.append_to_sheet(sheet_title, [ticket_row])
            
            if result['success']:
                logger.info(f"✓ Ticket logged to Google Sheets")
            
            return result
            
        except Exception as e:
            logger.error(f"Error logging to Sheets: {e}")
            return {'success': False, 'error': str(e)}
    
    def process_support_email(self, email_data: dict):
        """Main method to process support email"""
        try:
            logger.info(f"🎫 Processing support email...")
            logger.info(f"  From: {email_data.get('from_email')}")
            logger.info(f"  Subject: {email_data.get('subject')}")
            
            # Step 1: Categorize email
            category = self.categorize_email(
                email_data.get('subject', ''),
                email_data.get('body', '')
            )
            logger.info(f"  Category: {category.title()}")
            
            # Step 2: Generate ticket ID
            ticket_id = self.generate_ticket_id()
            
            # Step 3: Create support ticket
            ticket_result = self.create_support_ticket(
                email_data,
                category,
                ticket_id
            )
            
            if ticket_result['success']:
                # Step 4: Log to Google Sheets
                ticket_data = {
                    'ticket_id': ticket_id,
                    'customer_name': email_data.get('from_name', 'Unknown'),
                    'customer_email': email_data.get('from_email', ''),
                    'category': category,
                    'priority': 'High' if category == 'urgent' else 'Normal',
                    'created': datetime.now().isoformat(),
                    'doc_link': ticket_result.get('doc_link', '')
                }
                
                self.log_ticket_to_drive(ticket_data)
                
                self.tickets_processed += 1
                
                return {
                    'success': True,
                    'ticket_id': ticket_id,
                    'category': category,
                    'message': f'Support ticket {ticket_id} created. Auto-response pending approval.'
                }
            else:
                return ticket_result
                
        except Exception as e:
            logger.error(f"Error processing support email: {e}")
            return {'success': False, 'error': str(e)}


def main():
    """Test Customer Support AI"""
    print("="*60)
    print("Customer Support AI Agent - Test Mode")
    print("="*60)
    
    support_ai = CustomerSupportAI()
    
    if support_ai.authenticate():
        print("\n✓ Authentication successful")
        
        # Test with sample email
        test_email = {
            'from_name': 'John Doe',
            'from_email': 'john@example.com',
            'subject': 'Urgent: Website is down!',
            'body': 'Hi, our website has been down for the past hour. This is critical for our business. Please help ASAP!'
        }
        
        result = support_ai.process_support_email(test_email)
        
        if result['success']:
            print(f"\n✅ Support ticket created successfully!")
            print(f"  Ticket ID: {result['ticket_id']}")
            print(f"  Category: {result['category']}")
            print(f"  Message: {result['message']}")
        else:
            print(f"\n❌ Error: {result.get('error')}")
    else:
        print("\n❌ Authentication failed")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
