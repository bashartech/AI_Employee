---
name: "facebook-automation"
description: "Complete Facebook page automation with post monitoring, comment detection, lead scoring, auto-reply, Odoo CRM integration, and approval workflow"
---

# Facebook Automation - Complete Guide

## Overview

This automation handles the **complete Facebook engagement workflow**:
1. **Monitor** Facebook page posts
2. **Detect** new comments automatically
3. **Score** leads (0-100 based on interest)
4. **Save** to Odoo CRM as leads
5. **Generate** AI responses
6. **Create** approval files
7. **Post** replies (with approval)
8. **Send** follow-up emails/WhatsApp

---

## Quick Start

### Step 1: Installation (First Time Only)

```bash
# Facebook Graph API
pip install facebook-sdk

# Odoo integration
pip install xmlrpc-client

# For WhatsApp follow-ups
npm install whatsapp-web.js qrcode-terminal
```

### Step 2: Facebook App Setup

1. **Create Facebook App:**
   - Go to: https://developers.facebook.com/
   - Create App → Business
   - Add Product: Facebook Login

2. **Get Access Token:**
   - Go to: https://developers.facebook.com/tools/explorer/
   - Select your app
   - Permissions needed:
     - `pages_read_engagement`
     - `pages_manage_posts`
     - `pages_read_user_content`
   - Generate Access Token

3. **Configure:**
   Edit `config.py`:
   ```python
   FACEBOOK_PAGE_ID = "your_page_id"
   FACEBOOK_ACCESS_TOKEN = "your_access_token"
   ```

### Step 3: Odoo Configuration

Edit `config.py`:
```python
ODOO_URL = "https://your-company.odoo.com"
ODOO_DB = "your_database"
ODOO_USERNAME = "your_email@example.com"
ODOO_API_KEY = "your_api_key"
```

### Step 4: Start Automation

```bash
# Keep running (monitors Facebook)
python facebook_watcher.py

# Keep running (processes approvals)
python execute_approved.py
```

---

## Workflow (Automatic)

```
Facebook Comment Received
       ↓
Facebook Watcher (every 5 min)
       ↓
Analyze Comment
┌─────────────────────────────────────────┐
│ Comment Analysis                        │
│ - Extract user name                     │
│ - Extract comment text                  │
│ - Detect interest level                 │
│ - Check for spam                        │
└─────────────────────────────────────────┘
       ↓
Calculate Lead Score
┌─────────────────────────────────────────┐
│ Scoring Criteria                        │
│ +30: Asking about price/pricing         │
│ +25: Interested in product/service      │
│ +20: Request for demo/trial             │
│ +15: Company/business inquiry           │
│ +10: General inquiry                    │
│ -50: Spam/irrelevant                    │
└─────────────────────────────────────────┘
       ↓
Create Facebook Comment Task
┌─────────────────────────────────────────┐
│ Task File: Needs Action/                │
│ FACEBOOK_COMMENT_*.md                   │
│ - Comment ID                            │
│ - User Name                             │
│ - Comment Text                          │
│ - Lead Score                            │
│ - Timestamp                             │
└─────────────────────────────────────────┘
       ↓
Process Comment (Claude Code)
┌─────────────────────────────────────────┐
│ Claude Code Actions                     │
│ 1. Generate AI response                 │
│ 2. Create Odoo lead (if score >= 50)    │
│ 3. Create email approval                │
│ 4. Create WhatsApp approval (HOT leads) │
│ 5. Create Facebook reply approval       │
└─────────────────────────────────────────┘
       ↓
Create Approval Files
┌─────────────────────────────────────────┐
│ Pending Approval/                       │
│ - ODOO_LEAD_facebook_*.md               │
│ - APPROVAL_send_email_facebook_*.md     │
│ - APPROVAL_send_whatsapp_facebook_*.md  │
│ - APPROVAL_facebook_reply_*.md          │
└─────────────────────────────────────────┘
       ↓
Human Reviews & Approves
       ↓
Move to Approved/ Folder
       ↓
execute_approved.py Processes
┌─────────────────────────────────────────┐
│ Automatic Actions                       │
│ - Create Odoo lead                      │
│ - Send follow-up email                  │
│ - Send WhatsApp (HOT leads only)        │
│ - Post Facebook reply                   │
└─────────────────────────────────────────┘
       ↓
Move to Done/
```

---

## Commands Summary

| Action | Command |
|--------|---------|
| Start Facebook monitoring | `python facebook_watcher.py` |
| Process Facebook comments | `Process Facebook comments` |
| Send approved actions | **Automatic** (via `execute_approved.py`) |

**Keep these running:**
```bash
# Terminal 1: Facebook watcher
python facebook_watcher.py

# Terminal 2: Approval executor
python execute_approved.py
```

---

## Lead Scoring System

### Score Calculation (0-100)

| Signal | Points | Example |
|--------|--------|---------|
| **Price Inquiry** | +30 | "How much does it cost?" |
| **Product Interest** | +25 | "I'm interested in your service" |
| **Demo Request** | +20 | "Can I get a demo?" |
| **Business Inquiry** | +15 | "We're a company looking for..." |
| **General Inquiry** | +10 | "Tell me more about..." |
| **Contact Request** | +10 | "How can I contact you?" |
| **Spam/Irrelevant** | -50 | "Check out my page!" |

### Lead Categories

| Score | Category | Actions |
|-------|----------|---------|
| **80-100** | 🔥 HOT | Odoo Lead + Email + WhatsApp + Reply |
| **60-79** | ⚠️ WARM | Odoo Lead + Email + Reply |
| **40-59** | 📋 NORMAL | Odoo Lead + Reply |
| **< 40** | 💬 GENERAL | Reply only |

---

## Comment Analysis

### High-Intent Keywords

**Price/Buying Signals:**
- price, cost, pricing, how much, expensive, affordable
- buy, purchase, order, payment, invoice
- discount, offer, deal, promotion

**Interest Signals:**
- interested, want, need, looking for
- demo, trial, test, try
- enterprise, business, company, team
- subscription, plan, package

**Spam Signals:**
- check out my page
- visit my website
- click here for free
- make money fast
- work from home

---

## Approval File Formats

### Odoo Lead Approval (Facebook)

```markdown
---
type: odoo_lead_approval
action: create_lead
lead_name: Facebook Lead - John Doe
email: john.doe@email.com
phone: +1234567890
source: Facebook Page Comment
lead_score: 75
---

# Odoo Lead Creation Approval

## Lead Details

**Name:** Facebook Lead - John Doe
**Email:** john.doe@email.com
**Phone:** +1234567890
**Source:** Facebook Page Comment
**Lead Score:** 75/100 (WARM)

## Original Comment

"Hi, I'm interested in your Enterprise plan. 
Can you send me pricing details for a team of 50?"

## AI-Generated Response

"Hi John! Thanks for your interest in our Enterprise plan. 
I'll send you detailed pricing information via email. 
Our team will also reach out to discuss your specific needs!"

---

## Instructions
1. **Review** the lead details above
2. **Edit** if needed (add email/phone when available)
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder
```

### Email Notification Approval

```markdown
---
type: email_approval
action: send_email
to: sales@yourcompany.com
subject: 🎯 New Facebook Lead - John Doe (Score: 75/100)
---

# Email Notification Approval

## Email Body

NEW FACEBOOK LEAD!

─────────────────────────────
LEAD DETAILS
─────────────────────────────
Name: John Doe
Source: Facebook Page Comment
Lead Score: 75/100 (WARM)

─────────────────────────────
COMMENT
─────────────────────────────
"Hi, I'm interested in your Enterprise plan. 
Can you send me pricing details for a team of 50?"

─────────────────────────────
AI-GENERATED RESPONSE
─────────────────────────────
"Hi John! Thanks for your interest in our Enterprise plan. 
I'll send you detailed pricing information via email."

─────────────────────────────
ACTION REQUIRED
─────────────────────────────
1. Lead saved to Odoo CRM (separate approval)
2. Send personalized follow-up email
3. Respond within 1 hour for best conversion

---
AI Employee Vault
Lead Detection System

---

## Instructions
1. **Review** the notification email above
2. **Edit** recipient email if needed
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder
```

### WhatsApp Approval (HOT Leads Only)

```markdown
---
type: whatsapp_approval
action: send_whatsapp
phone: +1234567890
---

# WhatsApp Hot Lead Alert

## Message

🎯 HOT FACEBOOK LEAD!

Name: John Doe
Comment: "Hi, I'm interested in your Enterprise plan..."

Lead Score: 85/100

Respond within 1 hour!

---

## Instructions
1. **Review** the WhatsApp alert above
2. **Edit** phone number if needed
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder
```

### Facebook Reply Approval

```markdown
---
type: facebook_approval
action: facebook_reply
comment_id: 12345678901234567_8901234567890123
lead_score: 75
---

# Facebook Comment Reply Approval

## Comment ID to Reply

12345678901234567_8901234567890123

## AI-Generated Response

Hi John! Thanks for your interest in our Enterprise plan. 
I'll send you detailed pricing information via email. 
Our team will also reach out to discuss your specific needs!

## Lead Score

75/100 (WARM)

---

## Instructions
1. **Review** the AI-generated response above
2. **Edit** if needed
3. **Approve:** Move to `Approved/` folder
4. **Reject:** Move to `Rejected/` folder
```

---

## Odoo Integration

### Lead Creation

**Automatic for scores >= 40:**

```python
# Lead data structure
lead_data = {
    'name': f'Facebook Lead - {user_name}',
    'email': extracted_email or '',
    'phone': extracted_phone or '',
    'source': 'Facebook Page',
    'description': comment_text,
    'lead_score': score,
    'priority': 'high' if score >= 80 else 'normal'
}
```

### Lead File Created

```markdown
# Odoo Lead Created

**Name:** Facebook Lead - John Doe
**Email:** john.doe@email.com
**Phone:** +1234567890
**Source:** Facebook Page Comment
**Lead Score:** 75/100
**Odoo ID:** 12345
**Created:** 2026-03-27T12:00:00
**Original Comment:** "Interested in Enterprise plan..."
```

---

## Example Workflows

### Example 1: HOT Lead (Score 85+)

**Facebook Comment:**
```
John Doe
"Hi! I'm the CTO at TechCorp (500 employees). 
We're looking for an enterprise solution. 
Can you send pricing and schedule a demo?
My email: john@techcorp.com"
```

**Automation Flow:**

1. **Facebook Watcher** detects comment
2. **Analyzes** comment:
   - Enterprise inquiry: +15
   - Demo request: +20
   - Price inquiry: +30
   - Company info: +15
   - Contact provided: +5
   - **Total Score: 85/100 (HOT)** 🔥
3. **Creates task:** `Needs Action/FACEBOOK_COMMENT_*.md`
4. **Claude Code** processes:
   - Creates Odoo lead approval
   - Creates email notification
   - Creates WhatsApp alert (HOT lead!)
   - Creates Facebook reply
5. **You** approve all files
6. **Automatic actions:**
   - ✅ Odoo lead created
   - ✅ Email sent to sales team
   - ✅ WhatsApp sent to lead
   - ✅ Facebook reply posted

**Odoo Lead Created:**
```markdown
**Name:** Facebook Lead - John Doe
**Email:** john@techcorp.com
**Phone:** (to be collected)
**Company:** TechCorp
**Employees:** 500
**Position:** CTO
**Interest:** Enterprise Solution
**Lead Score:** 85/100 (HOT)
**Priority:** High
**Next Action:** Schedule demo call
```

**WhatsApp Sent:**
```
🎯 HOT FACEBOOK LEAD!

Name: John Doe
Company: TechCorp (500 employees)
Comment: "Hi! I'm the CTO at TechCorp..."

Lead Score: 85/100

Respond within 1 hour!
```

**Facebook Reply Posted:**
```
Hi John! Thanks for your interest in our Enterprise solution. 
I've sent detailed pricing to your email. Our team will also 
reach out within the hour to schedule a demo! 🚀
```

---

### Example 2: WARM Lead (Score 60-79)

**Facebook Comment:**
```
Sarah Smith
"Your product looks interesting! 
How much does it cost for small businesses?"
```

**Automation Flow:**

1. **Detects** comment
2. **Scores:**
   - Product interest: +25
   - Price inquiry: +30
   - Small business: +10
   - **Total: 65/100 (WARM)** ⚠️
3. **Creates** Odoo lead + Email + Reply
4. **No WhatsApp** (not HOT enough)
5. **You** approve
6. **Actions:**
   - ✅ Odoo lead created
   - ✅ Email sent to sales
   - ✅ Facebook reply posted

---

### Example 3: GENERAL Inquiry (Score < 60)

**Facebook Comment:**
```
Mike Johnson
"Nice post! Do you have a blog?"
```

**Automation Flow:**

1. **Detects** comment
2. **Scores:**
   - General inquiry: +10
   - **Total: 10/100 (GENERAL)** 💬
3. **Creates** Facebook reply only
4. **No Odoo lead** (too low score)
5. **No email/WhatsApp**
6. **You** approve reply
7. **Action:**
   - ✅ Facebook reply posted

**Reply Posted:**
```
Thanks Mike! Yes, we have a blog at yourcompany.com/blog 
Check it out for tips and updates! 📝
```

---

## Folder Structure

```
AI_Employee_Vault/
├── Needs Action/
│   └── FACEBOOK_COMMENT_*.md    # New comments
├── Pending Approval/
│   ├── ODOO_LEAD_facebook_*.md  # Odoo leads
│   ├── APPROVAL_send_email_facebook_*.md
│   ├── APPROVAL_send_whatsapp_facebook_*.md
│   └── APPROVAL_facebook_reply_*.md
├── Approved/
│   └── [Move files here to process]
├── Done/
│   └── EXECUTED_*.md            # Processed logs
├── Odoo_Data/
│   └── Leads/
│       └── LEAD_facebook_*.md   # Created leads
└── services/
    └── facebook_manager.py      # Facebook API
```

---

## Response Templates

### HOT Lead Response (80-100)
```markdown
Hi [Name]! Thanks for your interest! 🎯

I've sent detailed information to your email. 
Our team will reach out within 1 hour to discuss your needs!

Looking forward to working with you! 🚀
```

### WARM Lead Response (60-79)
```markdown
Hi [Name]! Great to hear from you!

I'll send you more information via email. 
Feel free to ask any questions!

Talk soon! 😊
```

### GENERAL Response (< 60)
```markdown
Hi [Name]! Thanks for your comment!

[Helpful answer to their question]

Let us know if you need anything else! 👍
```

---

## Lead Scoring Configuration

### Customize Scoring Weights

Edit `facebook_manager.py`:

```python
LEAD_SCORING = {
    'price_inquiry': 30,      # "how much", "pricing", "cost"
    'product_interest': 25,   # "interested", "want", "need"
    'demo_request': 20,       # "demo", "trial", "test"
    'business_inquiry': 15,   # "company", "business", "enterprise"
    'general_inquiry': 10,    # "tell me more", "info"
    'contact_provided': 5,    # Email/phone in comment
    'spam_detected': -50      # Spam keywords
}
```

### Customize Lead Categories

```python
LEAD_CATEGORIES = {
    'hot': {'min': 80, 'actions': ['odoo', 'email', 'whatsapp', 'reply']},
    'warm': {'min': 60, 'actions': ['odoo', 'email', 'reply']},
    'normal': {'min': 40, 'actions': ['odoo', 'reply']},
    'general': {'min': 0, 'actions': ['reply']}
}
```

---

## Email Templates

### Internal Sales Notification
```markdown
NEW FACEBOOK LEAD!

─────────────────────────────
LEAD DETAILS
─────────────────────────────
Name: [Name]
Source: Facebook Page Comment
Lead Score: [Score]/100 ([Category])

─────────────────────────────
COMMENT
─────────────────────────────
[Original comment text]

─────────────────────────────
AI-GENERATED RESPONSE
─────────────────────────────
[Response that was posted]

─────────────────────────────
ACTION REQUIRED
─────────────────────────────
1. Lead saved to Odoo CRM
2. Send personalized follow-up email
3. Respond within 1 hour for best conversion

---
AI Employee Vault
Lead Detection System
```

### Follow-up Email to Lead
```markdown
Subject: Thanks for your interest in [Product]!

Hi [Name],

Thanks for reaching out on Facebook!

[Personalized response to their inquiry]

I'd love to schedule a quick call to discuss your needs.
Are you available [suggest 2-3 time slots]?

Looking forward to connecting!

Best regards,
[Your Name]
[Your Position]
[Company]
[Phone]
```

---

## WhatsApp Templates

### HOT Lead Alert
```markdown
🎯 HOT FACEBOOK LEAD!

Name: [Name]
Comment: [Comment text...]

Lead Score: [Score]/100

Respond within 1 hour!
```

### Follow-up WhatsApp
```markdown
Hi [Name]! 👋

This is [Your Name] from [Company].

Saw your comment on our Facebook post about [topic].

I'd love to help you with [their need]. 

Are you free for a quick call today?

Best,
[Your Name]
[Phone]
```

---

## Troubleshooting

### Comments Not Detected

**Problem:** Comments posted but not detected

**Solutions:**
1. Check Facebook watcher is running: `python facebook_watcher.py`
2. Verify access token is valid (not expired)
3. Check page ID is correct in `config.py`
4. Verify app has `pages_read_engagement` permission

### Lead Score Too Low

**Problem:** Interested lead scored < 40

**Solutions:**
1. Edit comment task file manually
2. Update lead_score in YAML frontmatter
3. Re-run lead creation

### Odoo Lead Not Created

**Problem:** Score >= 40 but no lead

**Solutions:**
1. Check Odoo credentials in `config.py`
2. Verify Odoo API access
3. Check lead approval file
4. Manually approve lead creation

### Facebook Reply Not Posted

**Problem:** Approval moved but reply not posted

**Solutions:**
1. Check `execute_approved.py` is running
2. Verify Facebook reply approval format
3. Check comment_id is valid
4. Review executor logs for errors

---

## Best Practices

### Response Time

| Lead Category | Target Response |
|---------------|-----------------|
| HOT (80-100) | < 1 hour |
| WARM (60-79) | < 4 hours |
| NORMAL (40-59) | < 24 hours |
| GENERAL (< 40) | < 48 hours |

### Comment Monitoring

**Check frequency:**
- High-traffic pages: Every 2 minutes
- Medium pages: Every 5 minutes
- Low-traffic pages: Every 15 minutes

**Business hours:**
- Monitor 24/7 for HOT leads
- Business hours only for GENERAL

### Lead Handoff

**When to escalate:**
- ✅ HOT leads (80+) → Sales team immediately
- ✅ WARM leads (60-79) → Sales team within 4 hours
- ✅ Company size > 100 → Enterprise team
- ✅ C-level executive → Priority handling

**Information to collect:**
- Company name
- Company size
- Budget range
- Timeline
- Decision maker
- Current solution
- Pain points

---

## Metrics & Reporting

### Key Metrics

| Metric | Target | Calculation |
|--------|--------|-------------|
| Response Time | < 4 hours | Avg time to reply |
| Lead Conversion | > 15% | Comments → Customers |
| HOT Lead Close Rate | > 30% | HOT → Customers |
| Engagement Rate | > 5% | Comments / Post Reach |

### Daily Report Template

```markdown
# Facebook Leads Daily Report

## Summary
- Total Comments: XX
- HOT Leads: XX
- WARM Leads: XX
- Replies Posted: XX

## Leads by Score
- 80-100 (HOT): XX
- 60-79 (WARM): XX
- 40-59 (NORMAL): XX
- < 40 (GENERAL): XX

## Top Comments
1. [Comment 1] - Score: XX
2. [Comment 2] - Score: XX
3. [Comment 3] - Score: XX

## Actions Taken
- Odoo Leads Created: XX
- Emails Sent: XX
- WhatsApp Sent: XX
- Replies Posted: XX
```

---

## Advanced Configuration

### Custom Response Generation

Edit response generation in Claude Code prompt:

```python
prompt = f"""
You are a professional AI automation expert.

Someone commented on our Facebook page:
"{comment_text}"

Generate a professional, helpful response that:
1. Acknowledges their specific interest/need
2. Mentions our expertise (2 sentences max)
3. Invites them to send a message for details
4. Tone: Friendly and professional
5. Keep it under 150 characters
6. Do NOT use hashtags or emojis (unless HOT lead)
"""
```

### Spam Detection

Add custom spam filters:

```python
SPAM_KEYWORDS = [
    'check out my page',
    'visit my website',
    'click here for free',
    'make money fast',
    'work from home',
    'crypto investment',
    'forex trading'
]

def is_spam(comment_text):
    text_lower = comment_text.lower()
    return any(keyword in text_lower for keyword in SPAM_KEYWORDS)
```

### Auto-Reply for Common Questions

```python
AUTO_REPLIES = {
    'price': "Hi! Pricing starts at $X/month. I'll send detailed info via email!",
    'demo': "We'd love to show you a demo! When are you available?",
    'features': "Our key features include X, Y, Z. What specific features interest you?",
    'support': "Our support team is available 24/7. How can we help?"
}

def get_auto_reply(comment_text):
    text_lower = comment_text.lower()
    for keyword, reply in AUTO_REPLIES.items():
        if keyword in text_lower:
            return reply
    return None  # Use AI generation
```

---

## API Reference

### Facebook Comment Detection

```python
from services.facebook_manager import FacebookManager

fb = FacebookManager()

# Get recent comments
comments = fb.get_page_comments(page_id, limit=10)

# Analyze comment
analysis = fb.analyze_comment(comment)
# Returns: {
#     'user_name': '...',
#     'comment_text': '...',
#     'lead_score': 75,
#     'category': 'WARM',
#     'is_spam': False
# }
```

### Odoo Lead Creation

```python
from mcp_servers.odoo_server import OdooMCPServer

odoo = OdooMCPServer()

lead = odoo.create_lead(
    name='Facebook Lead - John Doe',
    email='john@example.com',
    phone='+1234567890',
    source='Facebook Page',
    description='Comment text...',
    lead_score=75
)

# Returns: {'success': True, 'lead_id': 12345}
```

### Post Facebook Reply

```python
from services.facebook_manager import FacebookManager

fb = FacebookManager()

result = fb.reply_to_comment(
    comment_id='12345678901234567_8901234567890123',
    message='Hi! Thanks for your interest!'
)

# Returns: {'success': True, 'reply_id': '...'}
```

---

## Related Skills

- [`odoo`](../odoo/SKILL.md) - Odoo CRM integration
- [`whatsapp-automation`](../whatsapp-automation/SKILL.md) - WhatsApp messaging
- [`email-automation`](../email-automation/SKILL.md) - Email processing
- [`hr-resume-automation`](../hr-resume-automation/SKILL.md) - HR automation
- [`customer-support-automation`](../customer-support-automation/SKILL.md) - Support tickets

---

## Support

**Common Issues:**
- Comments not detected → Check access token
- Lead score wrong → Edit task file manually
- Odoo lead failed → Check API credentials
- Reply not posted → Verify comment_id

**Logs Location:**
```
Logs/facebook_watcher.log
Logs/orchestrator.log
Logs/execute_approved.log
```
