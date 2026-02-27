# AI Employee Vault - Complete Setup & Implementation Guide

## Table of Contents

1. [System Overview](#system-overview)
2. [WhatsApp System](#whatsapp-system)
3. [Email System](#email-system)
4. [Approval Workflow](#approval-workflow)
5. [Agent Skills](#agent-skills)
6. [Troubleshooting](#troubleshooting)

---

## System Overview

The AI Employee Vault monitors multiple communication channels (WhatsApp, Email) and processes incoming messages with human-in-the-loop approval for all outgoing responses.

**Architecture:**
```
Incoming Message → Watcher Detects → Task Created → Claude Processes → Approval Request → Human Approves → Action Executed → Logged
```

**Key Components:**
- **Watchers:** Monitor incoming messages (WhatsApp, Gmail)
- **Task System:** Needs_Action → Pending_Approval → Approved → Done
- **Queue System:** Send_Queue for outgoing messages
- **Agent Skills:** Markdown files defining workflows for Claude

---

## WhatsApp System

### Overview

The WhatsApp system monitors incoming messages and provides smart auto-replies with full approval workflow for detailed responses.

### Components

**1. WhatsApp Watcher (`whatsapp_watcher_node.js`)**
- Monitors WhatsApp Web for incoming messages
- Implements smart auto-reply (first time or 3+ hours gap)
- Creates task files in Needs_Action/
- Processes Send_Queue every 5 seconds

**2. Contact Tracker (`whatsapp_contacts_tracker.json`)**
- Tracks last message time for each contact
- Enables smart auto-reply logic

**3. Send Queue (`Send_Queue/`)**
- Queue files for outgoing messages
- Processed automatically by watcher

### Setup Instructions

#### Prerequisites
```bash
# Install Node.js dependencies
npm install whatsapp-web.js qrcode-terminal
```

#### Step 1: First Time Authentication

```bash
# Start the watcher
node whatsapp_watcher_node.js
```

**What happens:**
1. Browser window opens with QR code
2. Scan QR code with your WhatsApp phone
3. Session saved in `whatsapp_session_js/`
4. Watcher starts monitoring

**Terminal output:**
```
============================================================
WhatsApp Watcher Started
============================================================
Vault: D:\DATA\HACKATHON_0\AI_Employee_Vault
Status: ✓ Connected and monitoring
Mode: Capturing ALL incoming messages
Queue: Checking Send_Queue every 5 seconds

Press Ctrl+C to stop
```

#### Step 2: How It Works

**When someone sends you a message:**

1. **Message Detection** (Automatic)
   ```
   📱 New WhatsApp message received!
      From: John Doe
      Message: Hello, can you help me?
      Time: 2026-02-13T18:00:00.000Z
      🤖 Auto-reply: YES (first time or 3+ hours gap)
      ✅ Auto-reply queued: QUEUE_autoreply_923001234567_...
   ✅ Task created: WHATSAPP_John_Doe_...
   ```

2. **Auto-Reply Sent** (Within 5-10 seconds)
   ```
   📤 Sending queued message...
      To: 923001234567
      Message: Thank you for your message! Bashar will respond...
   ✅ Message sent successfully!
      Moved to Done/QUEUE_autoreply_923001234567_..._SENT.md
   ```

3. **Task File Created** (`Needs_Action/WHATSAPP_John_Doe_...md`)
   ```yaml
   ---
   type: whatsapp
   from: John Doe
   phone: 923001234567
   received: 2026-02-13T18:00:00.000Z
   auto_reply_sent: true
   ---

   # WhatsApp Message from John Doe

   ## Message Content
   Hello, can you help me?
   ```

#### Step 3: Processing Messages

**Tell Claude:** "Process WhatsApp tasks"

Claude will:
1. Read all WhatsApp tasks in Needs_Action/
2. Analyze each message
3. Draft appropriate responses
4. Create approval requests in Pending_Approval/

#### Step 4: Approval Workflow

**Review approval file:** `Pending_Approval/APPROVAL_send_whatsapp_...md`

**If approved:**
```bash
move Pending_Approval\APPROVAL_send_whatsapp_*.md Approved\
```

**Tell Claude:** "Execute approved actions"

Claude will:
1. Read approved WhatsApp files
2. Create queue files in Send_Queue/
3. Watcher automatically sends within 5-10 seconds
4. Execution logged in Done/
5. Dashboard updated

### Smart Auto-Reply Logic

**Auto-reply is sent when:**
- ✅ First time someone messages you
- ✅ 3+ hours since their last message

**Auto-reply is NOT sent when:**
- ❌ Recent conversation (less than 3 hours)

**Example Timeline:**
```
10:00 AM - Person sends "Hi" → Auto-reply sent ✅
10:05 AM - Person sends "How are you?" → No auto-reply ❌
10:10 AM - Person sends "Are you there?" → No auto-reply ❌
2:00 PM - Person sends "Hello again" → Auto-reply sent ✅ (4 hours passed)
```

### File Structure

```
AI_Employee_Vault/
├── whatsapp_watcher_node.js          # Main watcher
├── whatsapp_contacts_tracker.json    # Contact tracking
├── whatsapp_session_js/              # Session data
├── Needs_Action/
│   └── WHATSAPP_*.md                 # Incoming message tasks
├── Send_Queue/
│   └── QUEUE_*.md                    # Outgoing message queue
├── Pending_Approval/
│   └── APPROVAL_send_whatsapp_*.md   # Awaiting approval
├── Approved/
│   └── APPROVAL_send_whatsapp_*.md   # Approved actions
└── Done/
    ├── QUEUE_*_SENT.md               # Sent messages
    └── EXECUTED_*.md                 # Execution logs
```

---

## Email System

### Overview

The Email system monitors Gmail inbox and sends emails via Gmail API with approval workflow.

### Components

**1. Gmail Watcher (`gmail_watcher.py`)**
- Monitors Gmail inbox for new emails
- Creates task files in Needs_Action/
- Uses Gmail API with OAuth 2.0

**2. Email Sender (`send_email.js`)**
- Sends emails via Gmail API
- Command-line interface
- Returns success/failure status

**3. Gmail Credentials**
- `credentials.json` - OAuth 2.0 client credentials
- `token.json` - Access token (auto-generated)

### Setup Instructions

#### Prerequisites

**1. Enable Gmail API:**
- Go to https://console.cloud.google.com/
- Create new project or select existing
- Enable Gmail API
- Create OAuth 2.0 credentials (Desktop app)
- Download credentials.json

**2. Install Dependencies:**
```bash
# Python dependencies
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client

# Node.js dependencies
npm install googleapis
```

#### Step 1: Setup Gmail Watcher

**Place credentials.json in project root**

**Run watcher for first time:**
```bash
python gmail_watcher.py
```

**What happens:**
1. Browser opens for Google authentication
2. Grant permissions (read + send)
3. Token saved as token.json
4. Watcher starts monitoring

**Terminal output:**
```
Gmail Watcher Started
Checking for new emails every 60 seconds...
Press Ctrl+C to stop
```

#### Step 2: How It Works

**When you receive an email:**

1. **Email Detection** (Every 60 seconds)
   ```
   New email from: john@example.com
   Subject: Project Update
   Creating task file...
   Task created: EMAIL_john_example_com_1739470000.md
   ```

2. **Task File Created** (`Needs_Action/EMAIL_john_example_com_...md`)
   ```yaml
   ---
   type: email
   from: john@example.com
   subject: Project Update
   received: 2026-02-13T18:00:00.000Z
   ---

   # Email from john@example.com

   ## Subject
   Project Update

   ## Body
   Hi, I wanted to update you on the project status...
   ```

#### Step 3: Processing Emails

**Tell Claude:** "Process email tasks"

Claude will:
1. Read all email tasks in Needs_Action/
2. Analyze each email
3. Draft appropriate responses
4. Create approval requests in Pending_Approval/

#### Step 4: Sending Emails

**Review approval file:** `Pending_Approval/APPROVAL_send_email_...md`

**If approved:**
```bash
move Pending_Approval\APPROVAL_send_email_*.md Approved\
```

**Tell Claude:** "Execute approved actions"

Claude will:
1. Read approved email files
2. Execute: `node send_email.js "to@example.com" "Subject" "Body"`
3. Log execution in Done/
4. Update Dashboard

### Manual Email Sending

**Command line:**
```bash
node send_email.js "recipient@example.com" "Subject Line" "Email body content here"
```

**Example:**
```bash
node send_email.js "john@example.com" "Re: Project Update" "Thanks for the update! The project looks great."
```

### File Structure

```
AI_Employee_Vault/
├── gmail_watcher.py                  # Gmail monitor
├── send_email.js                     # Email sender
├── credentials.json                  # OAuth credentials
├── token.json                        # Access token
├── Needs_Action/
│   └── EMAIL_*.md                    # Incoming email tasks
├── Pending_Approval/
│   └── APPROVAL_send_email_*.md      # Awaiting approval
├── Approved/
│   └── APPROVAL_send_email_*.md      # Approved actions
└── Done/
    └── EXECUTED_*.md                 # Execution logs
```

---

## Approval Workflow

### Overview

All outgoing communications require human approval before sending.

### Workflow Steps

**1. Task Creation**
- Watcher detects incoming message
- Task file created in Needs_Action/

**2. Processing**
- User: "Process [whatsapp/email] tasks"
- Claude analyzes and drafts responses
- Approval request created in Pending_Approval/

**3. Review**
- Human reviews drafted response
- Can edit if needed
- Moves to Approved/ when ready

**4. Execution**
- User: "Execute approved actions"
- Claude sends the message
- Execution logged in Done/
- Dashboard updated

### Approval File Format

**WhatsApp Approval:**
```yaml
---
type: approval_request
action: send_whatsapp
to: 923001234567
contact: John Doe
created: 2026-02-13T18:00:00.000Z
status: pending
---

# WhatsApp Reply Approval Required

## Contact Details
**Name:** John Doe
**Phone:** 923001234567

## Original Message
Hello, can you help me?

## Drafted Response
Hi John! Yes, I'd be happy to help. What do you need assistance with?

## Context
**Why this response:** Friendly acknowledgment and invitation to share details
**Tone:** Professional and helpful
**Expected outcome:** They will explain their request

## To Approve
Move this file to `Approved` folder

## To Reject
Move this file to `Rejected` folder (or edit the response and re-save)
```

**Email Approval:**
```yaml
---
type: approval_request
action: send_email
to: john@example.com
subject: Re: Project Update
created: 2026-02-13T18:00:00.000Z
status: pending
---

# Email Send Approval Required

## Recipient
**To:** john@example.com
**Subject:** Re: Project Update

## Original Email
[Original email content]

## Drafted Response
Thanks for the update! The project looks great. I have a few questions...

## Context
**Why this response:** Acknowledges update and opens dialogue
**Tone:** Professional and collaborative

## To Approve
Move this file to `Approved` folder
```

---

## Agent Skills

Agent Skills are markdown files that define workflows for Claude to follow.

### Available Skills

**1. process_tasks.md**
- General task processing
- Scans Needs_Action folder
- Updates Dashboard

**2. Process_WhatsApp_Message.md**
- Processes WhatsApp tasks
- Drafts responses
- Creates approval requests

**3. Process_Email_Message.md**
- Processes email tasks
- Drafts responses
- Creates approval requests

**4. Execute_Approved_WhatsApp.md**
- Executes approved WhatsApp messages
- Creates queue files
- Logs execution

**5. Execute_Approved_Email.md**
- Executes approved emails
- Sends via send_email.js
- Logs execution

### How to Use Agent Skills

**Tell Claude:**
- "Process WhatsApp tasks" → Uses Process_WhatsApp_Message.md
- "Process email tasks" → Uses Process_Email_Message.md
- "Execute approved actions" → Uses Execute_Approved_WhatsApp.md + Execute_Approved_Email.md

---

## Troubleshooting

### WhatsApp Issues

**Problem: QR code not appearing**
```bash
# Delete session and restart
rmdir /s /q whatsapp_session_js
node whatsapp_watcher_node.js
```

**Problem: Messages not being detected**
- Check watcher is running
- Check terminal for errors
- Verify WhatsApp Web is connected

**Problem: Auto-reply not sending**
- Check Send_Queue folder has queue files
- Check watcher terminal for errors
- Verify queue file format is correct

**Problem: Queue files not processing**
- Check watcher shows "Queue: Checking Send_Queue every 5 seconds"
- Check for error messages in terminal
- Verify queue file has correct YAML format

### Email Issues

**Problem: Gmail authentication failed**
```bash
# Delete token and re-authenticate
rm token.json
python gmail_watcher.py
```

**Problem: Insufficient permissions**
- Check credentials.json has correct scopes
- Delete token.json and re-authenticate
- Ensure Gmail API is enabled in Google Cloud Console

**Problem: Email not sending**
```bash
# Test manually
node send_email.js "your@email.com" "Test" "Test message"
```

### General Issues

**Problem: Task files not being created**
- Check watcher is running
- Check folder permissions
- Verify Needs_Action folder exists

**Problem: Approval workflow not working**
- Check file is in correct folder (Pending_Approval → Approved)
- Verify file format is correct
- Check Claude has access to folders

---

## Best Practices

### Running Watchers

**Start both watchers in separate terminals:**

Terminal 1:
```bash
node whatsapp_watcher_node.js
```

Terminal 2:
```bash
python gmail_watcher.py
```

**Keep them running 24/7 for continuous monitoring**

### Processing Tasks

**Regular schedule:**
- Check Needs_Action every 2-4 hours
- Process tasks: "Process WhatsApp tasks" and "Process email tasks"
- Review approvals in Pending_Approval
- Execute approved actions

### Monitoring

**Check Dashboard.md regularly:**
- Shows all completed tasks
- Tracks system activity
- Identifies patterns

**Check watcher terminals:**
- Monitor for errors
- Verify messages are being detected
- Check auto-replies are sending

---

## Quick Reference

### Commands

**Start Watchers:**
```bash
node whatsapp_watcher_node.js
python gmail_watcher.py
```

**Process Tasks:**
- "Process WhatsApp tasks"
- "Process email tasks"

**Execute Actions:**
- "Execute approved actions"

**Manual Sending:**
```bash
node send_email.js "to@example.com" "Subject" "Body"
```

### Folder Structure

```
Needs_Action/     → Incoming tasks
Pending_Approval/ → Awaiting review
Approved/         → Ready to execute
Done/             → Completed tasks
Send_Queue/       → Outgoing WhatsApp messages
```

### File Naming

```
WHATSAPP_[contact]_[timestamp].md
EMAIL_[sender]_[timestamp].md
APPROVAL_send_whatsapp_[timestamp].md
APPROVAL_send_email_[timestamp].md
EXECUTED_[original_filename].md
QUEUE_[type]_[phone]_[timestamp].md
```

---

## Silver Tier Requirements ✅

This implementation satisfies all Silver Tier requirements:

- ✅ **2+ Watchers:** WhatsApp + Gmail
- ✅ **MCP Server:** send_email.js + send_whatsapp.js (functional equivalent)
- ✅ **Human-in-the-Loop:** Approval workflow (Pending_Approval → Approved)
- ✅ **Basic Scheduling:** Watchers run continuously, queue processed every 5 seconds
- ✅ **Agent Skills:** Multiple .md files defining workflows

---

## Support

For issues or questions:
1. Check Troubleshooting section
2. Review watcher terminal output
3. Verify file formats and folder structure
4. Check Dashboard.md for system status
