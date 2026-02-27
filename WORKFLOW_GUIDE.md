# AI Employee Vault - Complete Workflow Guide

## Overview

This system processes tasks through a human-in-the-loop approval workflow:

```
Inbox → Needs Action → Pending Approval → [Human Approves] → Approved → Executor → Done
```

## Folder Structure

```
AI_Employee_Vault/
├── Inbox/              ← Drop raw files here (auto-processed by watch_inbox.py)
├── Needs Action/       ← New tasks appear here (process with Qwen/Claude)
├── Pending Approval/   ← Tasks awaiting your review
├── Approved/           ← Move approved tasks here (auto-executed)
├── Done/               ← Completed tasks
└── Rejected/           ← Rejected tasks
```

## Complete Workflow

### Step 1: Create/Receive a Task

**Option A: Drop a file in Inbox/**
```
# Create a file: Inbox/task.txt
send email to bashartecg56@gmail.com for wedding attendance
```
→ Automatically moved to `Needs Action/` by `watch_inbox.py`

**Option B: Create directly in Needs Action/**
```
# Create: Needs Action/send_wedding_email.md
send email to bashartecg56@gmail.com confirming wedding attendance
```

### Step 2: Process Task with AI (Qwen/Claude Code)

Use your AI assistant to process the task:

```bash
# For Qwen users
ollama run qwen2.5:latest "Process the task in Needs Action/send_wedding_email.md using Agent_Skills/Process_Email_Message.md"

# For Claude Code users
claude "Process the task in Needs Action/send_wedding_email.md using Agent_Skills/Process_Email_Message.md"
```

**AI will:**
1. Read the task
2. Determine it's an email task
3. Draft a professional email response
4. Create an approval request file in `Pending Approval/`

### Step 3: Review Approval Request

The AI creates a file like:
```
Pending Approval/APPROVAL_send_email_20260217_232711.md
```

**Review the drafted email:**
- Check recipient email
- Verify subject line
- Review email body content
- Ensure tone is appropriate

### Step 4: Approve or Reject

**To Approve:**
```
Move file from: Pending Approval/APPROVAL_send_email_*.md
Move file to:   Approved/APPROVAL_send_email_*.md
```

**To Reject:**
```
Move file to: Rejected/ folder
```

**To Edit:**
```
1. Edit the file in Pending Approval/
2. Modify the email content
3. Then move to Approved/
```

### Step 5: Automatic Execution

**The executor (`execute_approved.py`) automatically:**
1. Detects the file in `Approved/` folder
2. Extracts: `to`, `subject`, `body` from the approval file
3. Runs: `node send_email.js "to" "subject" "body"`
4. Creates execution log in `Done/`
5. Moves approval file to `Done/`

**No manual command needed!**

### Step 6: Check Results

Check `Done/` folder for execution logs:
```
Done/EXECUTED_APPROVAL_send_email_20260217_232711.md
```

This file contains:
- Original approval request
- Execution status (success/failed)
- Email message ID
- Timestamp

## Running the Executors

### Email/WhatsApp/LinkedIn Executor

**Option 1: Run continuously (recommended)**
```bash
python execute_approved.py
# or
run_executor.bat
```

**Option 2: Run once**
```bash
python -c "from execute_approved import ApprovedExecutor; e = ApprovedExecutor(); e.process_all_approved()"
```

### Inbox Watcher

Watches `Inbox/` folder for new files:
```bash
python watch_inbox.py
```

### Full Automation

Run all watchers:
```bash
run_all_watchers.bat
```

## Task Types

### 1. Email Tasks

**File pattern:** `APPROVAL_send_email_*.md`

**Required fields:**
```yaml
---
type: approval_request
action: send_email
to: recipient@example.com
subject: Email subject
---

## Email Body

Email content here...
```

**Execution:** `node send_email.js "to" "subject" "body"`

### 2. WhatsApp Tasks

**File pattern:** `APPROVAL_send_whatsapp_*.md`

**Required fields:**
```yaml
---
type: approval_request
action: send_whatsapp
phone: 923001234567
---

## WhatsApp Message

Message content here...
```

**Execution:** `node send_whatsapp.js "phone" "message"`

### 3. LinkedIn Tasks

**File pattern:** `LINKEDIN_POST_*.md` or `APPROVAL_linkedin_*.md`

**Execution:** Uses `engine/linkedin_poster.py`

## Agent Skills

Located in `Agent_Skills/` folder:

| Skill | Purpose |
|-------|---------|
| `Process_Email_Message.md` | Draft email responses |
| `Execute_Approved_Email.md` | Execute approved emails |
| `Process_WhatsApp_Message.md` | Draft WhatsApp responses |
| `Execute_Approved_WhatsApp.md` | Execute approved WhatsApp |
| `process_tasks.md` | Master workflow guide |

## Example: Complete Email Workflow

### 1. Create Task
```
# File: Inbox/wedding.txt
send email to bashartecg56@gmail.com for attending the wedding
```

### 2. AI Processes (Qwen/Claude)
```bash
# AI reads task and creates:
Pending Approval/APPROVAL_send_email_20260217_232711.md
```

### 3. Human Reviews
```
# User reads the drafted email
# Moves file to Approved/
```

### 4. Executor Sends
```
# execute_approved.py detects file in Approved/
# Runs: node send_email.js "bashartecg56@gmail.com" "Wedding..." "Dear Friend..."
# Email sent! Message ID: 19c6cf0e374e2e5a
```

### 5. Logged in Done/
```
Done/EXECUTED_APPROVAL_send_email_20260217_232711.md
Done/APPROVAL_send_email_20260217_232711.md
```

## Troubleshooting

### Email not sending

**Check:**
1. Is `execute_approved.py` running?
2. Is the file in `Approved/` folder?
3. Does the file have correct YAML frontmatter (`to:`, `subject:`)?
4. Is `send_email.js` working? Test: `node send_email.js "test@example.com" "Test" "Body"`

### WhatsApp not sending

**Check:**
1. WhatsApp session authenticated?
2. Phone number format correct?
3. `send_whatsapp.js` working?

### LinkedIn not posting

**Check:**
1. LinkedIn credentials configured?
2. `engine/linkedin_poster.py` working?

### Task not processed by AI

**Run manually:**
```bash
# For Qwen
ollama run qwen2.5:latest "Process task in Needs Action/your_task.md"

# For Claude Code
claude "Process task in Needs Action/your_task.md"
```

## Quick Commands

| Command | Purpose |
|---------|---------|
| `python watch_inbox.py` | Watch Inbox for new files |
| `python execute_approved.py` | Execute approved actions |
| `python run_automation.py` | Full automation orchestrator |
| `python dashboard.py` | View dashboard |
| `run_executor.bat` | Start executor (Windows) |
| `run_all_watchers.bat` | Start all watchers |

## Best Practices

1. **Always review before approving** - Check email/message content
2. **Keep executor running** - Run `execute_approved.py` in background
3. **Use Agent Skills** - Follow the templates in `Agent_Skills/`
4. **Check execution logs** - Review files in `Done/` folder
5. **Clean up regularly** - Move processed files from `Done/` to archive

---

*AI Employee Vault - Automated Task Processing System*
