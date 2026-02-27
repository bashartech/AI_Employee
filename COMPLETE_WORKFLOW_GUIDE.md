# 🚀 Complete Workflow Guide - AI Employee Vault
## Bronze + Silver + Gold Tier - Manual Operation Guide

**Last Updated:** February 24, 2026  
**Status:** ✅ All Tiers Operational

**NEW:** LinkedIn Lead Automation - Comments/messages auto-detected and created as leads in Odoo!

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Bronze Tier - Foundation](#bronze-tier)
3. [Silver Tier - Communication](#silver-tier)
4. [Gold Tier - Business Management](#gold-tier)
5. [Complete Daily Workflow](#daily-workflow)
6. [Complete Weekly Workflow](#weekly-workflow)
7. [Command Reference](#command-reference)
8. [Troubleshooting](#troubleshooting)

---

## 📌 Overview

Your AI Employee Vault has **3 tiers** of functionality:

| Tier | Purpose | Components |
|------|---------|------------|
| **Bronze** | Foundation | File handling, folder structure, basic automation |
| **Silver** | Communication | Gmail, WhatsApp, LinkedIn automation |
| **Gold** | Business Management | Odoo CRM, Sales, Invoicing, CEO Briefings |

---

## 🥉 Bronze Tier - Foundation

### What It Does
- Organizes all tasks in folders
- Tracks what needs action, what's approved, what's done
- Provides dashboard and logging

### Folder Structure
```
AI_Employee_Vault/
├── Inbox/              ← Drop files here for processing
├── Needs Action/       ← New tasks appear here
├── Pending Approval/   ← AI drafts responses here
├── Approved/           ← Move files here to execute
├── Done/               ← Completed tasks go here
├── Rejected/           ← Rejected tasks go here
├── Logs/               ← Audit logs stored here
└── Odoo_Data/          ← Gold tier data (Leads, Invoices, etc.)
```

### How It Works (Manual)

**Step 1: Drop a File**
- Create a text file with your request
- Drop it in `Inbox/` folder
- Example: `task.txt` with content "Follow up with client John"

**Step 2: Watcher Processes It**
```bash
# Run inbox watcher (keep running)
python watch_inbox.py
```
- File moves to `Needs Action/`
- Task file created with metadata

**Step 3: Process the Task**
- Open file from `Needs Action/`
- Add your notes
- Move to `Pending Approval/` or handle manually

---

## 🥈 Silver Tier - Communication Automation

### Components Working

| Component | Script | Purpose | Status |
|-----------|--------|---------|--------|
| **Gmail Watcher** | `gmail_watcher.py` | Monitors Gmail for new emails | ✅ Working |
| **Gmail Sender** | `send_email.js` | Sends emails via Gmail API | ✅ Working |
| **WhatsApp Watcher** | `whatsapp_watcher_node.js` | Monitors WhatsApp Web | ✅ Working |
| **WhatsApp Sender** | `whatsapp_watcher_node.js` | Sends WhatsApp messages | ✅ Working |
| **LinkedIn Poster** | `engine/linkedin_poster.py` | Posts to LinkedIn | ✅ Working |
| **Executor** | `execute_approved.py` | Executes all approved actions | ✅ Working |

---

### 📧 Gmail Automation - Step by Step

#### **Automatic Email Detection**

**Step 1: Start Gmail Watcher**
```bash
python gmail_watcher.py
```
**Keep this terminal running!**

**What happens:**
- Checks Gmail every 2 minutes
- Looks for unread emails
- Creates task files in `Needs Action/`

**Example Output:**
```
[15:30:45] Found 1 new email(s)
✓ Created task: EMAIL_19c7fa84.md
  From: client@example.com
  Subject: Pricing inquiry
```

---

#### **Process Email Manually**

**Step 2: Read the Email Task**
- Open: `Needs Action/EMAIL_*.md`
- Read the email content
- Decide on response

**Step 3: Ask AI to Draft Response**
Give me this prompt:
```
Process email from Needs Action folder
```

**What I do:**
- Read email from `Needs Action/`
- Draft professional response
- Create approval file in `Pending Approval/`

**Example Output:**
```
Created: Pending Approval/APPROVAL_send_email_20260224_1530.md
```

---

#### **Review and Send**

**Step 4: Review Draft**
- Open: `Pending Approval/APPROVAL_send_email_*.md`
- Read the drafted response
- Edit if needed (tone, content, etc.)

**Step 5: Approve to Send**
- Move file from `Pending Approval/` to `Approved/`
- **That's it!** The executor will send it.

**Step 6: Executor Sends Email**
```bash
# Run executor (keep running)
python execute_approved.py
```

**What executor does:**
- Checks `Approved/` folder every 5 seconds
- Finds email approval files
- Runs: `node send_email.js`
- Email sent via Gmail!
- Moves file to `Done/`

**Example Output:**
```
[EMAIL] Executing: APPROVAL_send_email_20260224_1530.md
[EMAIL] Sending to: client@example.com
✅ Email sent successfully!
[DONE] Moved APPROVAL_send_email_20260224_1530.md to Done/
```

---

### 📱 WhatsApp Automation - Step by Step

#### **Automatic Message Detection**

**Step 1: Start WhatsApp Watcher**
```bash
node whatsapp_watcher_node.js
```
**Keep this terminal running!**

**What happens:**
- Monitors WhatsApp Web
- Auto-replies to new contacts (first time or 3+ hours gap)
- Creates task files in `Needs Action/`

**Example Output:**
```
[15:45:30] New message from 923001234567
✓ Created task: WHATSAPP_923001234567_20260224.md
```

---

#### **Process WhatsApp Message**

**Step 2: Read the Message Task**
- Open: `Needs Action/WHATSAPP_*.md`
- Read the WhatsApp message
- Decide on response

**Step 3: Ask AI to Draft Response**
Give me this prompt:
```
Process WhatsApp messages
```

**What I do:**
- Read message from `Needs Action/`
- Draft response
- Create approval file in `Pending Approval/`

---

#### **Review and Send**

**Step 4: Review Draft**
- Open: `Pending Approval/APPROVAL_send_whatsapp_*.md`
- Read the drafted message
- Edit if needed

**Step 5: Approve to Send**
- Move file from `Pending Approval/` to `Approved/`

**Step 6: Executor Sends WhatsApp**
```bash
# Executor must be running
python execute_approved.py
```

**What executor does:**
- Finds WhatsApp approval in `Approved/`
- Adds to `Send_Queue/` folder
- WhatsApp watcher detects queue item
- Sends via WhatsApp Web!
- Moves file to `Done/`

**Example Output:**
```
[WHATSAPP] Processing: APPROVAL_send_whatsapp_*.md
[WHATSAPP] Added to Send_Queue: QUEUE_approved_923001234567.md
[WHATSAPP] whatsapp_watcher_node.js will send it automatically
```

---

### 💼 LinkedIn Automation - Step by Step

#### **Create LinkedIn Post**

**Step 1: Ask AI to Create Post**
Give me this prompt:
```
Create LinkedIn post about [your topic]
```

**Example:**
```
Create LinkedIn post about our new AI services
```

**What I do:**
- Generate professional post content
- Add hashtags and formatting
- Create approval file in `Pending Approval/`

**Example Output:**
```
Created: Pending Approval/APPROVAL_linkedin_post_20260224.md
```

---

#### **Review and Publish**

**Step 2: Review Post**
- Open: `Pending Approval/APPROVAL_linkedin_post_*.md`
- Read the post content
- Edit if needed (add image, modify text)
- Optional: Add image path in metadata

**Step 3: Approve to Publish**
- Move file from `Pending Approval/` to `Approved/`

**Step 4: Executor Publishes**
```bash
# Executor must be running
python execute_approved.py
```

**What executor does:**
- Finds LinkedIn approval in `Approved/`
- Runs: `python engine/linkedin_poster.py`
- Browser opens automatically
- Logs into LinkedIn (session saved)
- Posts content!
- Moves file to `Done/`

**Example Output:**
```
[LINKEDIN] Executing: APPROVAL_linkedin_post_20260224.md
📝 Creating LinkedIn post...
✅ Post published successfully!
[DONE] Moved APPROVAL_linkedin_post_20260224.md to Done/
```

---

## 🥇 Gold Tier - Business Management (Odoo)

### Components Working

| Component | Script | Purpose | Status |
|-----------|--------|---------|--------|
| **Odoo MCP Server** | `mcp_servers/odoo_server.py` | Connects to Odoo | ✅ Working |
| **CRM Integration** | `odoo_server.py` | Create/manage leads | ✅ Working |
| **Sales Integration** | `odoo_server.py` | Create quotations | ✅ Working |
| **Invoice Integration** | `odoo_server.py` | Create invoices | ✅ Working |
| **CEO Briefing** | `engine/ceo_briefing.py` | Weekly reports | ✅ Working |
| **Scheduler** | `scheduler.py` | Automated tasks | ✅ Working |
| **Audit Logger** | `engine/audit_logger.py` | Logs all actions | ✅ Working |

---

### 🎯 Create Lead in Odoo CRM

**Step 1: Ask AI to Create Lead**
Give me this prompt:
```
Create lead in Odoo for [Name] - [Email] - [Phone] - Source: [LinkedIn/Website/Referral]
```

**Example:**
```
Create lead in Odoo for Sarah Khan - sarah@techcorp.com - +923009876543 - Source: LinkedIn
```

**What I do:**
- Extract lead details
- Create approval file in `Pending Approval/`

**Example Output:**
```
Created: Pending Approval/ODOO_LEAD_sarah_20260224.md
```

---

**Step 2: Review Lead Details**
- Open: `Pending Approval/ODOO_LEAD_*.md`
- Verify: Name, Email, Phone, Source
- Edit if needed

**Step 3: Approve to Create**
- Move file from `Pending Approval/` to `Approved/`

**Step 4: Executor Creates Lead**
```bash
# Executor must be running
python execute_approved.py
```

**What executor does:**
- Finds Odoo lead approval in `Approved/`
- Calls: `odoo.create_lead()`
- Lead created in Odoo CRM!
- Saves details to `Odoo_Data/Leads/`
- Logs action to audit log
- Moves file to `Done/`

**Example Output:**
```
[ODOO] Executing: ODOO_LEAD_sarah_20260224.md
✅ Odoo connected successfully (UID: 2)
✅ Lead created: Sarah Khan (ID: 46)
[DONE] Moved ODOO_LEAD_sarah_20260224.md to Done/
```

**Where to See in Odoo:**
1. Open: `http://localhost:8069`
2. Login
3. Click **CRM** app
4. Find lead: "Sarah Khan" (ID: 46)

---

### 💰 Create Invoice in Odoo

**Step 1: Ask AI to Create Invoice**
Give me this prompt:
```
Create invoice in Odoo for [Customer] - [Email] - Amount: [X] - Description: [Service/Product]
```

**Example:**
```
Create invoice in Odoo for Tech Solutions - info@techsolutions.com - Amount: 75000 - Web Development Services
```

**What I do:**
- Extract invoice details
- Check if customer exists (by email)
- Create customer if new
- Create approval file in `Pending Approval/`

**Example Output:**
```
Created: Pending Approval/ODOO_INV_tech_20260224.md
```

---

**Step 2: Review Invoice Details**
- Open: `Pending Approval/ODOO_INV_*.md`
- Verify: Customer, Amount, Description
- Edit if needed

**Step 3: Approve to Create**
- Move file from `Pending Approval/` to `Approved/`

**Step 4: Executor Creates Invoice**
```bash
# Executor must be running
python execute_approved.py
```

**What executor does:**
- Finds Odoo invoice approval in `Approved/`
- Calls: `odoo.create_invoice()`
- Invoice created in Odoo!
- Saves details to `Odoo_Data/Invoices/`
- Logs action
- Moves file to `Done/`

**Example Output:**
```
[ODOO] Executing Invoice: ODOO_INV_tech_20260224.md
✅ Invoice created: ID INV/2026/00025
[DONE] Moved ODOO_INV_tech_20260224.md to Done/
```

**Where to See in Odoo:**
1. Open: `http://localhost:8069`
2. Login
3. Click **Invoicing** app
4. Find invoice: `INV/2026/00025`

---

### 📊 Generate CEO Weekly Briefing

**Option 1: Generate Manually**

**Step 1: Ask AI to Generate**
Give me this prompt:
```
Generate CEO weekly briefing
```

**What I do:**
- Connect to Odoo
- Fetch: Revenue, Unpaid Invoices, Leads, Quotations
- Generate comprehensive briefing
- Save to `Odoo_Data/CEO_Briefings/`

**Example Output:**
```
✅ CEO Briefing generated: CEO_Briefing_2026-02-24.md
📁 Saved to: Odoo_Data/CEO_Briefings/CEO_Briefing_2026-02-24.md
```

**What's in the Briefing:**
- Revenue summary (this week)
- Unpaid invoices (follow-up list)
- Recent CRM leads
- Sales quotations
- Action items
- Quick stats

---

**Option 2: Schedule Automatically**

**Step 1: Start Scheduler**
```bash
python scheduler.py
```
**Keep this terminal running!**

**What happens:**
- Runs every Monday at 8:00 AM
- Generates CEO briefing automatically
- Saves to `Odoo_Data/CEO_Briefings/`
- You get notified

**To Change Schedule:**
Edit `scheduler.py`:
```python
# Change from Monday 8 AM to Sunday 9 AM
schedule.every().sunday.at("09:00").do(run_ceo_briefing)
```

---

## 🔄 Complete Daily Workflow (Manual Operation)

### Morning Routine (9:00 AM)

**Step 1: Start All Watchers**

Open 4 terminals:

**Terminal 1 - Gmail Watcher:**
```bash
cd D:\DATA\HACKATHON_0\AI_Employee_Vault
python gmail_watcher.py
```

**Terminal 2 - WhatsApp Watcher:**
```bash
cd D:\DATA\HACKATHON_0\AI_Employee_Vault
node whatsapp_watcher_node.js
```

**Terminal 3 - Executor:**
```bash
cd D:\DATA\HACKATHON_0\AI_Employee_Vault
python execute_approved.py
```

**Terminal 4 - Scheduler (Optional):**
```bash
cd D:\DATA\HACKATHON_0\AI_Employee_Vault
python scheduler.py
```

**Or use batch files:**
```bash
# Start all watchers
run_all_watchers.bat

# Start executor
run_executor.bat
```

---

**Step 2: Check Overnight Activity**

Check these folders:
1. `Needs Action/` - New emails/messages?
2. `Inbox/` - Any files dropped?

**If files found:**
- Open each file
- Read content
- Decide action needed

---

**Step 3: Process Communications**

**For Emails:**
```
Prompt: Process email messages
```

**For WhatsApp:**
```
Prompt: Process WhatsApp messages
```

**What happens:**
- I read from `Needs Action/`
- Draft responses
- Create files in `Pending Approval/`

---

**Step 4: Review and Approve**

**Check:** `Pending Approval/` folder

**For each file:**
1. Open and read
2. Edit if needed
3. Move to `Approved/` to execute
4. Or move to `Rejected/` to discard

**Executor automatically:**
- Detects files in `Approved/`
- Executes them (sends email/WhatsApp/posts LinkedIn/creates Odoo records)
- Moves to `Done/`

---

**Step 5: Check Odoo Data**

**Check:**
- `Odoo_Data/Leads/` - New leads created?
- `Odoo_Data/Invoices/` - New invoices created?
- `Odoo_Data/Quotations/` - New quotations?

**Review and follow up in Odoo:**
- Open: `http://localhost:8069`
- Check CRM, Invoices, Sales

---

### Evening Routine (6:00 PM)

**Step 1: Check Audit Logs**

Open: `Logs/audit_2026-02-24.log`

**Look for:**
- Failed actions (status: failed)
- Errors to fix
- Success count

**Example:**
```bash
# Count today's actions
findstr "success" Logs\audit_2026-02-24.log | find /c /v ""

# Find failures
findstr "failed" Logs\audit_2026-02-24.log
```

---

**Step 2: Review Done Folder**

Check: `Done/` folder

**See what was completed today:**
- Emails sent
- WhatsApp messages sent
- LinkedIn posts published
- Odoo leads/invoices created

---

**Step 3: Plan Tomorrow**

**Create tasks for tomorrow:**
- Drop files in `Inbox/`
- Or create directly in `Needs Action/`

---

## 📅 Complete Weekly Workflow

### Monday Morning (8:00 AM)

**CEO Briefing Day!**

If scheduler is running:
- Briefing auto-generated at 8 AM
- Check: `Odoo_Data/CEO_Briefings/`

If manual:
```
Prompt: Generate CEO weekly briefing
```

**Review Briefing:**
- Revenue this week
- Unpaid invoices (21 in your case!)
- Recent leads
- Quotations status

**Action Items:**
- Follow up on unpaid invoices
- Contact new leads
- Review quotations

---

### Wednesday (Any Time)

**Research Meeting Day**
- Zoom meeting at 10:00 PM
- Learn from other AI Employee builders
- Share progress

---

### Friday Afternoon (4:00 PM)

**Weekly Review**

**Step 1: Check All Folders**
```
Needs Action/     → Should be empty or minimal
Pending Approval/ → Should be reviewed
Approved/         → Should be empty (executor processed)
Done/             → Archive or review
```

**Step 2: Review Audit Logs**
```bash
# Open weekly log
type Logs\audit_2026-02-*.log
```

**Step 3: Odoo Review**
- Open Odoo
- Check CRM pipeline
- Check unpaid invoices
- Check quotations

**Step 4: Plan Next Week**
- Create tasks for next week
- Drop in `Inbox/` or `Needs Action/`

---

## 🎯 Command Reference

### Start Commands

```bash
# Gmail Watcher
python gmail_watcher.py

# WhatsApp Watcher
node whatsapp_watcher_node.js

# Executor (All actions)
python execute_approved.py

# Scheduler (CEO briefings)
python scheduler.py

# Inbox Watcher
python watch_inbox.py

# All Watchers (Batch)
run_all_watchers.bat

# Executor (Batch)
run_executor.bat
```

---

### AI Prompts

**Email Processing:**
```
Process email messages
```

**WhatsApp Processing:**
```
Process WhatsApp messages
```

**LinkedIn Post:**
```
Create LinkedIn post about [topic]
```

**Odoo Lead:**
```
Create lead in Odoo for [Name] - [Email] - [Phone] - Source: [Source]
```

**Odoo Invoice:**
```
Create invoice in Odoo for [Customer] - [Email] - Amount: [X] - Description: [Service]
```

**Odoo Quotation:**
```
Create quotation in Odoo for [Customer] - [Email] - Amount: [X] - Products: [Products]
```

**CEO Briefing:**
```
Generate CEO weekly briefing
```

---

### Folder Movement

```
Inbox/ → Needs Action/     (Automatic by watcher)
Needs Action/ → Pending Approval/  (AI creates approval)
Pending Approval/ → Approved/      (You move after review)
Approved/ → Done/          (Executor moves after execution)
Pending Approval/ → Rejected/      (You move to discard)
```

---

## 🔧 Troubleshooting

### Gmail Not Detecting Emails

**Problem:** No emails showing in terminal

**Solution:**
1. Check watcher is running: `python gmail_watcher.py`
2. Verify Gmail has unread emails
3. Check token exists: `token.pickle`
4. Re-authenticate if needed:
   ```bash
   # Delete old token
   del token.pickle
   
   # Re-run watcher
   python gmail_watcher.py
   ```

---

### WhatsApp Not Sending

**Problem:** Message stuck in `Send_Queue/`

**Solution:**
1. Check WhatsApp watcher is running: `node whatsapp_watcher_node.js`
2. Check session exists: `whatsapp_session_js/`
3. Re-scan QR code if needed:
   ```bash
   # Delete session
   rmdir /s whatsapp_session_js
   
   # Re-run watcher
   node whatsapp_watcher_node.js
   # Scan QR code
   ```

---

### LinkedIn Not Posting

**Problem:** Browser closes without posting

**Solution:**
1. Check session exists: `linkedin_session/`
2. Re-login:
   ```bash
   python setup_linkedin.py
   # Login in browser
   ```
3. Check executor is running

---

### Odoo Connection Failed

**Problem:** "Odoo authentication failed"

**Solution:**
1. Check Odoo is running: `http://localhost:8069`
2. Verify credentials in `.env`:
   ```
   URL = http://localhost:8069
   Database = ai_employee_db
   Username = bashartech56@gmail.com
   Password = bashar320420
   ```
3. Test connection:
   ```bash
   python test_odoo.py
   ```

---

### Executor Not Detecting Files

**Problem:** Files in `Approved/` not being processed

**Solution:**
1. Check executor is running: `python execute_approved.py`
2. Check filename matches pattern:
   - Email: `APPROVAL_send_email_*.md`
   - WhatsApp: `APPROVAL_send_whatsapp_*.md`
   - LinkedIn: `APPROVAL_linkedin_*.md`
   - Odoo Lead: `ODOO_LEAD_*.md`
   - Odoo Invoice: `ODOO_INV_*.md`
3. Check file has correct `action:` in YAML frontmatter

---

## ✅ Daily Checklist

### Morning (9 AM)
- [ ] Start Gmail watcher
- [ ] Start WhatsApp watcher
- [ ] Start executor
- [ ] Check `Needs Action/` folder
- [ ] Process new emails/messages

### Afternoon (2 PM)
- [ ] Check `Pending Approval/` folder
- [ ] Review and approve drafts
- [ ] Move to `Approved/`
- [ ] Verify executor processed them

### Evening (6 PM)
- [ ] Check audit logs
- [ ] Review `Done/` folder
- [ ] Plan tomorrow's tasks
- [ ] Stop watchers (if not running 24/7)

---

## 📊 What's Working in Your System

| Feature | Status | Last Tested |
|---------|--------|-------------|
| **Gmail Watcher** | ✅ Working | Feb 24, 2026 |
| **Gmail Sender** | ✅ Working | Feb 24, 2026 |
| **WhatsApp Watcher** | ✅ Working | Feb 24, 2026 |
| **WhatsApp Sender** | ✅ Working | Feb 24, 2026 |
| **LinkedIn Poster** | ✅ Working | Feb 24, 2026 |
| **Odoo Connection** | ✅ Working (UID: 2) | Feb 24, 2026 |
| **Odoo Lead Creation** | ✅ Working (Lead ID: 45) | Feb 23, 2026 |
| **Odoo Invoice Fetch** | ✅ Working (21 unpaid) | Feb 24, 2026 |
| **Odoo Quotations** | ✅ Working (10 found) | Feb 24, 2026 |
| **CEO Briefing** | ✅ Working | Feb 24, 2026 |
| **Audit Logging** | ✅ Working | Feb 24, 2026 |
| **Executor** | ✅ Working | Feb 24, 2026 |

---

## 🎉 Summary

You have a **fully functional AI Employee** with:

✅ **Bronze Tier:** File handling, folder structure, logging  
✅ **Silver Tier:** Gmail, WhatsApp, LinkedIn automation  
✅ **Gold Tier:** Odoo CRM, Sales, Invoicing, CEO Briefings  

**Total Components:** 15+ scripts and integrations  
**Total Automation:** Email, WhatsApp, LinkedIn, Odoo  
**Total Logging:** Complete audit trail of all actions  

**Manual Operation:** All working via prompts and file movement  
**Ready for Automation:** Can be connected to Claude Code for full autonomy  

---

*Your AI Employee Vault is production-ready! 🚀*
