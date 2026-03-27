---
name: "customer-support-automation"
description: "Complete customer support automation with ticket creation, auto-response, lead detection, invoice/quotation generation in Odoo, and Google Workspace integration"
---

# Customer Support Automation - Complete Guide

## Overview

This automation handles the **complete customer support workflow**:
1. **Receive** support emails via Gmail
2. **Categorize** by urgency (Urgent/Billing/Technical/General)
3. **Create** support ticket (file + Google Doc)
4. **Log** to Google Sheets tracker
5. **Generate** AI response
6. **Send** auto-response (with approval)
7. **Create** Odoo lead/invoice if sales opportunity

---

## Quick Start

### Step 1: Installation (First Time Only)

```bash
# Core dependencies
pip install google-auth google-auth-oauthlib google-api-python-client

# Odoo integration (if using Odoo CRM)
pip install xmlrpc-client
```

### Step 2: Google Authentication

```bash
# Generate Google token
python generate_token.py
```
- Browser opens → Login to Google
- Authorize: Gmail, Sheets, Docs
- Token saved to `token.json`

### Step 3: Odoo Configuration (Optional)

Edit `config.py`:
```python
ODOO_URL = "https://your-company.odoo.com"
ODOO_DB = "your_database"
ODOO_USERNAME = "your_email@example.com"
ODOO_API_KEY = "your_api_key"
```

### Step 4: Start Automation

```bash
# Keep running (monitors Gmail)
python gmail_watcher.py

# Keep running (processes approvals)
python execute_approved.py
```

---

## Workflow (Automatic)

```
Support Email Received
       ↓
Gmail Watcher (every 2 min)
       ↓
Categorize Request
┌─────────────────────────────────────────┐
│ Category Detection                      │
│ - Urgent (asap, emergency, critical)    │
│ - Billing (invoice, payment, refund)    │
│ - Technical (bug, error, issue)         │
│ - Feature (request, suggestion)         │
│ - General (everything else)             │
└─────────────────────────────────────────┘
       ↓
Create Support Ticket
┌─────────────────────────────────────────┐
│ Ticket File: Support_Tickets/SUP-*.md   │
│ - Ticket ID: SUP-YYYYMMDDHHMMSS         │
│ - Category: urgent/billing/technical    │
│ - Priority: High/Normal                 │
│ - Customer Email                        │
│ - Subject                               │
│ - Full Content                          │
└─────────────────────────────────────────┘
       ↓
Google Doc Created
┌─────────────────────────────────────────┐
│ Support Ticket Document                 │
│ - Customer Details                      │
│ - Issue Description                     │
│ - Resolution Section                    │
│ - Notes Section                         │
└─────────────────────────────────────────┘
       ↓
Google Sheets Logged
┌─────────────────────────────────────────┐
│ Support Tickets Tracker                 │
│ - Ticket ID, Email, Subject             │
│ - Category, Priority, Status            │
│ - Created Date, Doc Link                │
└─────────────────────────────────────────┘
       ↓
AI Response Generated
┌─────────────────────────────────────────┐
│ Category-Specific Template              │
│ - Urgent: 1 hour response               │
│ - Billing: 4 hours response             │
│ - Technical: 24 hours response          │
│ - Feature: Under review                 │
│ - General: 24 hours response            │
└─────────────────────────────────────────┘
       ↓
Approval File Created
       ↓
Human Reviews & Approves
       ↓
Move to Approved/ Folder
       ↓
execute_approved.py Sends Email
       ↓
Check for Sales Opportunity
┌─────────────────────────────────────────┐
│ Lead Detection                          │
│ - Interested in product/service?        │
│ - Request for quote?                    │
│ - Enterprise inquiry?                   │
└─────────────────────────────────────────┘
       ↓
If Lead: Create Odoo Lead/Invoice
       ↓
Move to Done/
```

---

## Commands Summary

| Action | Command |
|--------|---------|
| Start Gmail monitoring | `python gmail_watcher.py` |
| Process support tickets | `Process support tickets` |
| Send approved responses | **Automatic** (via `execute_approved.py`) |
| Create Odoo lead | `Create Odoo lead from [ticket]` |

**Keep these running:**
```bash
# Terminal 1: Gmail watcher
python gmail_watcher.py

# Terminal 2: Approval executor
python execute_approved.py
```

---

## Email Categorization

### Category Keywords

| Category | Keywords | Priority | Response Time |
|----------|----------|----------|---------------|
| **Urgent** | urgent, asap, emergency, critical, down, broken, not working | High | 1 hour |
| **Billing** | invoice, payment, billing, refund, charge, price, cost | Normal | 4 hours |
| **Technical** | bug, error, issue, problem, technical, help, support | Normal | 24 hours |
| **Feature** | feature, request, suggestion, improvement, idea, add | Normal | Review |
| **General** | (everything else) | Normal | 24 hours |

### Auto-Response Templates

#### Urgent Category
```markdown
Dear Valued Customer,

Thank you for contacting us regarding this URGENT matter.

We understand the critical nature of your issue and have escalated it to our senior support team.

Ticket ID: SUP-YYYYMMDDHHMMSS
Priority: URGENT
Estimated Response: Within 1 hour

A senior engineer will contact you shortly.

Best regards,
Customer Support Team
```

#### Billing Category
```markdown
Dear Valued Customer,

Thank you for your inquiry regarding billing.

Our billing specialist has received your request and will review your account shortly.

Ticket ID: SUP-YYYYMMDDHHMMSS
Priority: Normal
Estimated Response: Within 4 hours during business hours

Best regards,
Billing Support Team
```

#### Technical Category
```markdown
Dear Valued Customer,

Thank you for contacting technical support.

We've received your request and a support engineer will investigate this issue.

Ticket ID: SUP-YYYYMMDDHHMMSS
Priority: Normal
Estimated Response: Within 24 hours

Best regards,
Technical Support Team
```

#### Feature Category
```markdown
Dear Valued Customer,

Thank you for your feature suggestion! We appreciate customers like you who help us improve.

Your feedback has been forwarded to our product team for consideration.

Ticket ID: SUP-YYYYMMDDHHMMSS
Status: Under Review

Best regards,
Product Team
```

#### General Category
```markdown
Dear Valued Customer,

Thank you for contacting us.

We've received your inquiry and will respond as soon as possible.

Ticket ID: SUP-YYYYMMDDHHMMSS
Priority: Normal
Estimated Response: Within 24 hours

Best regards,
Customer Support Team
```

---

## Support Ticket File Format

```markdown
---
type: support_ticket
ticket_id: SUP-20260327120000
category: technical
priority: normal
customer_email: customer@example.com
subject: Website not loading
created: 2026-03-27T12:00:00
status: new
---

# Support Ticket: SUP-20260327120000

## Customer Information
- **Email:** customer@example.com
- **Category:** Technical
- **Priority:** Normal
- **Created:** 2026-03-27 12:00:00

## Original Email
**Subject:** Website not loading

**Content:**
Hi,

Our website is showing a 500 error since this morning.
This is affecting our business operations.

Please help urgently.

Thanks,
Customer

## Resolution
[To be filled by support agent]

## Notes
[Add notes here]
```

---

## Google Sheets Integration

### Support Tickets Tracker Columns

| Column | Description |
|--------|-------------|
| Ticket ID | SUP-YYYYMMDDHHMMSS |
| Email | Customer email address |
| Subject | Email subject (truncated to 50 chars) |
| Category | urgent/billing/technical/feature/general |
| Priority | High/Normal |
| Created | Timestamp |
| Status | New/In Progress/Resolved/Closed |
| Doc Link | Google Doc URL |

### Access Tracker

```
https://docs.google.com/spreadsheets/d/[ID]/edit
```
(Spreadsheet created automatically on first ticket)

---

## Google Docs Integration

### Support Ticket Document Sections

1. **Ticket Header**
   - Ticket ID
   - Customer Email
   - Category, Priority
   - Created Date

2. **Original Issue**
   - Subject
   - Full email content
   - Attachments (if any)

3. **Resolution**
   - Steps taken
   - Solution provided
   - Time to resolve

4. **Notes**
   - Internal notes
   - Follow-up required
   - Escalation details

---

## Odoo Integration

### Lead Detection

**Automatic detection from support emails:**

| Trigger | Action |
|---------|--------|
| "pricing", "cost", "quote" | Create Odoo Lead |
| "enterprise", "business", "company" | Create Odoo Lead |
| "demo", "trial", "test" | Create Odoo Lead |
| "invoice", "bill", "payment" | Create/Update Odoo Invoice |
| "purchase", "buy", "order" | Create Odoo Quotation |

### Create Odoo Lead

**Command:**
```
Create Odoo lead from SUP-20260327120000
```

**Claude Code will:**
1. Read support ticket
2. Extract customer info
3. Create lead in Odoo CRM
4. Link ticket to lead
5. Log in `Odoo_Data/Leads/`

**Lead File Created:**
```markdown
# Odoo Lead Created

**Name:** Customer Inquiry - customer@example.com
**Email:** customer@example.com
**Phone:** (from ticket or empty)
**Source:** Support Ticket SUP-20260327120000
**Odoo ID:** 12345
**Created:** 2026-03-27T12:00:00
**Approval File:** APPROVAL_lead_*.md
```

### Create Odoo Invoice

**Command:**
```
Create invoice for customer@example.com amount $500
```

**Claude Code will:**
1. Find/create customer in Odoo
2. Create invoice line items
3. Generate invoice PDF
4. Email to customer
5. Log in `Odoo_Data/Invoices/`

### Create Odoo Quotation

**Command:**
```
Create quotation for customer@example.com for Enterprise Plan
```

**Claude Code will:**
1. Find/create customer in Odoo
2. Add products/services
3. Generate quotation PDF
4. Email to customer
5. Log in `Odoo_Data/Quotations/`

---

## Approval File Formats

### Support Response Approval

```markdown
---
type: email_approval
action: send_email
to: customer@example.com
subject: Re: Website not loading
ticket_id: SUP-20260327120000
category: technical
---

# Email Response Approval

## Customer Details
- **Email:** customer@example.com
- **Ticket ID:** SUP-20260327120000
- **Category:** Technical
- **Priority:** Normal

## AI-Generated Response

## Email Body

Dear Valued Customer,

Thank you for contacting technical support.

We've received your request and a support engineer will investigate this issue.

Ticket ID: SUP-20260327120000
Priority: Normal
Estimated Response: Within 24 hours

Best regards,
Technical Support Team

---

## Instructions
1. **Review** the AI-generated response above
2. **Edit** if needed for personalization
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder

## Notes
- This is an AI-generated auto-response
- For urgent tickets, consider personal follow-up
- Response will be sent automatically upon approval
- Google Doc: https://docs.google.com/...
```

### Odoo Lead Approval

```markdown
---
type: odoo_lead_approval
action: create_lead
lead_name: Customer Inquiry - customer@example.com
email: customer@example.com
phone: +1234567890
source: Support Ticket SUP-20260327120000
---

# Odoo Lead Creation Approval

## Lead Details

**Name:** Customer Inquiry - customer@example.com
**Email:** customer@example.com
**Phone:** +1234567890
**Source:** Support Ticket SUP-20260327120000
**Lead Score:** 50/100

## Original Comment

[Original support email content]

## AI-Generated Response

[Response that was sent]

---

## Instructions
1. **Review** the lead details above
2. **Edit** if needed (add email/phone when available)
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder
```

### Odoo Invoice Approval

```markdown
---
type: odoo_invoice_approval
action: create_invoice
customer_name: Customer Company
customer_email: customer@example.com
amount: 500
description: Monthly Subscription - Enterprise Plan
---

# Odoo Invoice Creation Approval

## Invoice Details

**Customer:** Customer Company
**Email:** customer@example.com
**Amount:** $500
**Description:** Monthly Subscription - Enterprise Plan

## Line Items
- Enterprise Plan (Monthly): $500

---

## Instructions
1. **Review** the invoice details above
2. **Edit** if needed
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder
```

---

## Folder Structure

```
AI_Employee_Vault/
├── Needs Action/
│   └── EMAIL_*.md                 # New support emails
├── Support_Tickets/
│   └── SUP-*.md                   # Created tickets
├── Pending Approval/
│   ├── APPROVAL_email_*.md        # Support responses
│   ├── APPROVAL_lead_*.md         # Odoo leads
│   ├── APPROVAL_invoice_*.md      # Odoo invoices
│   └── APPROVAL_quotation_*.md    # Odoo quotations
├── Approved/
│   └── [Move files here to process]
├── Done/
│   └── EXECUTED_*.md              # Processed logs
├── Odoo_Data/
│   ├── Leads/
│   ├── Invoices/
│   └── Quotations/
└── services/
    ├── customer_support_ai.py     # Support automation
    └── google/
        ├── sheets_service.py      # Google Sheets
        └── docs_service.py        # Google Docs
```

---

## Example Workflows

### Example 1: Technical Support Request

**Email received:**
```
From: customer@example.com
Subject: Website showing 500 error

Hi,

Our website www.example.com is showing a 500 error 
since this morning. This is affecting our business.

Please help urgently.

Thanks,
John
```

**Automation Flow:**

1. **Gmail Watcher** detects support email
2. **Categorizes** as "Technical" (keywords: error)
3. **Creates ticket:** `Support_Tickets/SUP-20260327120000.md`
4. **Google Doc** created with ticket details
5. **Google Sheets** logged
6. **AI Response** generated (Technical template)
7. **Approval file** created: `Pending Approval/APPROVAL_email_*.md`
8. **You** move to `Approved/`
9. **Executor** sends response email! ✅
10. **File** moved to `Done/`

**Response sent:**
```markdown
Dear John,

Thank you for contacting technical support.

We've received your request and a support engineer will investigate this issue.

Ticket ID: SUP-20260327120000
Priority: Normal
Estimated Response: Within 24 hours

Best regards,
Technical Support Team
```

---

### Example 2: Urgent Support Request

**Email received:**
```
From: urgent@example.com
Subject: URGENT: Production server down!

Our production server is DOWN since 30 minutes.
This is an EMERGENCY! We need help ASAP!

Server: prod-01.example.com
Error: Connection timeout

Please respond IMMEDIATELY!
```

**Automation Flow:**

1. **Detects** as "Urgent" (keywords: urgent, emergency, asap, down)
2. **Priority:** High
3. **Response time:** 1 hour
4. **Creates** ticket with HIGH priority
5. **Generates** urgent response template
6. **Creates** approval file
7. **You** approve → Email sent! ✅

**Response sent:**
```markdown
Dear Valued Customer,

Thank you for contacting us regarding this URGENT matter.

We understand the critical nature of your issue and have escalated it to our senior support team.

Ticket ID: SUP-20260327120100
Priority: URGENT
Estimated Response: Within 1 hour

A senior engineer will contact you shortly.

Best regards,
Customer Support Team
```

---

### Example 3: Sales Lead from Support

**Email received:**
```
From: business@company.com
Subject: Question about Enterprise pricing

Hi,

We're a company of 500 employees and interested in 
your Enterprise plan. Can you send us pricing details?

Also, do you offer volume discounts?

Thanks,
Sarah Johnson
CTO, Tech Company Inc.
```

**Automation Flow:**

1. **Detects** as "Billing" (keywords: pricing)
2. ** ALSO detects** as SALES LEAD (keywords: enterprise, company, pricing)
3. **Creates** support ticket
4. **Creates** Odoo Lead automatically
5. **Generates** billing response
6. **Creates** Odoo lead approval file
7. **You** approve both → Email sent + Lead created! ✅

**Odoo Lead Created:**
```markdown
**Name:** Enterprise Inquiry - Sarah Johnson
**Email:** business@company.com
**Phone:** (to be collected)
**Source:** Support Ticket SUP-20260327120200
**Company:** Tech Company Inc.
**Position:** CTO
**Employees:** 500
**Interest:** Enterprise Plan
```

---

## Troubleshooting

### Ticket Not Created

**Problem:** Email received but no ticket file

**Solutions:**
1. Check Gmail watcher is running: `python gmail_watcher.py`
2. Verify email not filtered as spam/promotional
3. Check `Needs Action/` folder for email task
4. Run: `Process support tickets`

### Wrong Category

**Problem:** Ticket categorized incorrectly

**Solutions:**
1. Edit ticket file manually
2. Update category in YAML frontmatter
3. Re-run response generation

### Google Sheets Not Updating

**Problem:** "Failed to log to tracker" error

**Solutions:**
1. Verify `token.json` has Sheets permission
2. Check internet connection
3. Re-run: `python generate_token.py`
4. Check spreadsheet not deleted

### Odoo Lead Not Created

**Problem:** Lead keywords detected but no lead created

**Solutions:**
1. Check Odoo credentials in `config.py`
2. Verify Odoo API access
3. Check lead approval file in `Pending Approval/`
4. Manually approve lead creation

---

## Best Practices

### Response Times

| Category | Target | Escalation |
|----------|--------|------------|
| Urgent | 1 hour | After 30 min → Manager |
| Billing | 4 hours | After 2 hours → Billing Team |
| Technical | 24 hours | After 12 hours → Senior Engineer |
| Feature | 48 hours | After 24 hours → Product Team |
| General | 24 hours | After 12 hours → Support Lead |

### Ticket Management

**Daily:**
- Review all new tickets
- Update status (New → In Progress → Resolved)
- Escalate urgent tickets

**Weekly:**
- Review unresolved tickets
- Check response time metrics
- Update knowledge base

**Monthly:**
- Analyze ticket trends
- Identify common issues
- Improve auto-responses

### Lead Handoff

**When to create Odoo lead:**
- ✅ Pricing inquiry
- ✅ Enterprise/business interest
- ✅ Demo/trial request
- ✅ Volume discount inquiry
- ✅ Partnership inquiry

**Lead information to collect:**
- Company name
- Company size
- Budget range
- Timeline
- Decision maker
- Current solution

---

## Metrics & Reporting

### Key Metrics

| Metric | Target | Calculation |
|--------|--------|-------------|
| Response Time | < 4 hours | Avg time to first response |
| Resolution Time | < 24 hours | Avg time to resolve |
| Customer Satisfaction | > 90% | Post-ticket survey |
| Lead Conversion | > 20% | Leads → Customers |

### Weekly Report Template

```markdown
# Support Weekly Report

## Summary
- Total Tickets: XX
- Resolved: XX
- In Progress: XX
- Avg Response Time: X hours

## By Category
- Urgent: XX
- Billing: XX
- Technical: XX
- Feature: XX
- General: XX

## Leads Generated
- New Leads: XX
- Converted: XX
- Pipeline Value: $XX,XXX

## Top Issues
1. [Issue 1] - XX tickets
2. [Issue 2] - XX tickets
3. [Issue 3] - XX tickets
```

---

## Advanced Configuration

### Custom Categories

Edit `customer_support_ai.py`:

```python
def _categorize_support_request(self, subject, body):
    text = (subject + " " + body).lower()
    
    # Add custom category
    if 'custom_keyword' in text:
        return 'custom_category'
    
    # ... existing categories
```

### Custom Response Templates

Edit `customer_support_ai.py`:

```python
templates = {
    'custom_category': """Dear Customer,

Custom response template here...

Best regards,
Support Team""",
    # ... existing templates
}
```

### Auto-Escalation Rules

Edit `customer_support_ai.py`:

```python
# Escalate if no response in X hours
ESCALATION_RULES = {
    'urgent': 0.5,      # 30 minutes
    'billing': 2,       # 2 hours
    'technical': 12,    # 12 hours
    'feature': 24,      # 24 hours
    'general': 12       # 12 hours
}
```

---

## API Reference

### Create Support Ticket

```python
from services.customer_support_ai import CustomerSupportAI

support = CustomerSupportAI()

ticket = support.create_ticket(
    email='customer@example.com',
    subject='Issue description',
    body='Full email content',
    category='technical'
)

# Returns: {'ticket_id': 'SUP-...', 'success': True}
```

### Log to Google Sheets

```python
from services.google.sheets_service import GoogleSheetsService

sheets = GoogleSheetsService()

result = sheets.get_or_create_spreadsheet('Support Tickets Tracker')
spreadsheet_id = result['id']

sheets.append_data(spreadsheet_id, 'Sheet1!A1', [ticket_row])
```

### Create Odoo Lead

```python
from mcp_servers.odoo_server import OdooMCPServer

odoo = OdooMCPServer()

lead = odoo.create_lead(
    name='Customer Inquiry',
    email='customer@example.com',
    phone='+1234567890',
    source='Support Ticket'
)

# Returns: {'success': True, 'lead_id': 12345}
```

---

## Related Skills

- [`hr-resume-automation`](../hr-resume-automation/SKILL.md) - HR hiring automation
- [`odoo`](../odoo/SKILL.md) - Odoo CRM/ERP integration
- [`email-automation`](../email-automation/SKILL.md) - General email processing

---

## Support

**Common Issues:**
- Ticket not created → Check Gmail watcher
- Wrong category → Edit ticket file manually
- Google Sheets error → Re-run `generate_token.py`
- Odoo lead failed → Check API credentials

**Logs Location:**
```
Logs/orchestrator.log
Logs/gmail_watcher.log
Logs/customer_support.log
```
