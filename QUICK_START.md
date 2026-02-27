# AI Employee Vault - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies (One-Time)
```bash
cd D:\DATA\HACKATHON_0\AI_Employee_Vault

# Python dependencies
pip install -r requirements.txt

# Node.js dependencies
npm install
```

### Step 2: Setup Credentials (One-Time)

**Gmail:**
```bash
python gmail_watcher.py
# Browser opens → Login to Google → Authorize
```

**WhatsApp:**
```bash
node whatsapp_watcher_node.js
# Browser opens → Scan QR code with phone
```

**LinkedIn:**
```bash
python setup_linkedin.py
# Browser opens → Login to LinkedIn
```

### Step 3: Start Executor (Runs Everything!)
```bash
python execute_approved.py
# or
run_executor.bat
```
**This automatically handles:**
- ✅ Approved emails → Sends via `send_email.js`
- ✅ Approved WhatsApp → Adds to queue
- ✅ Approved LinkedIn → Publishes via `linkedin_poster.py`

---

## 📋 How It Works (All Channels)

### The 5-Step Workflow

```
1. Message Received → Needs Action/
2. "Process [type] messages" → Pending Approval/
3. You review & approve → Approved/
4. "Execute approved actions" → Sent!
5. Files moved to Done/
```

---

## 📧 Email Automation

### Start Monitoring
```bash
python gmail_watcher.py
```

### Process Emails
```
# Tell Claude Code
Process email messages
```

### Send Approved (Automatic!)
```bash
# Start executor (keeps running)
python execute_approved.py
# or
run_executor.bat
```
**Executor automatically detects approved emails and sends them!** ✅

**More info:** `.claude/skills/email-automation/SKILL.md`

---

## 📱 WhatsApp Automation

### Start Monitoring (Keep Running!)
```bash
node whatsapp_watcher_node.js
# or
start_whatsapp.bat
```

### Process Messages
```
# Tell Claude Code
Process WhatsApp messages
```

### Send Approved (Automatic!)
The `whatsapp_watcher_node.js` automatically sends from queue every 5 seconds.

**Also run executor (optional - auto-approves):**
```bash
python execute_approved.py
# or
run_executor.bat
```

**More info:** `.claude/skills/whatsapp-automation/SKILL.md`

---

## 💼 LinkedIn Automation

### Setup (One-Time)
```bash
python setup_linkedin.py
```

### Create Post
```
# Tell Claude Code
Create LinkedIn post about [topic]
```

### Publish Post (Automatic!)
```bash
# Start executor (keeps running)
python execute_approved.py
# or
run_executor.bat
```
**Executor automatically detects approved posts and publishes them!** ✅

**More info:** `.claude/skills/linkedin-automation/SKILL.md`

---

## 📁 Folder Structure

```
AI_Employee_Vault/
├── Needs Action/        ← New messages/tasks appear here
├── Pending Approval/    ← Drafted responses (you review)
├── Approved/            ← Move approved items here
├── Done/                ← Completed items
├── Rejected/            ← Rejected items
├── Send_Queue/          ← WhatsApp messages waiting to send
└── Dashboard.md         ← Activity log
```

---

## 🎯 Quick Commands Reference

| Action | Command |
|--------|---------|
| **Email** | |
| Start monitoring | `python gmail_watcher.py` |
| Process emails | `Process email messages` |
| Send approved | **Automatic!** (via `execute_approved.py`) |
| **WhatsApp** | |
| Start monitoring | `node whatsapp_watcher_node.js` |
| Process messages | `Process WhatsApp messages` |
| Send approved | **Automatic!** (watcher sends from queue) |
| **LinkedIn** | |
| Setup login | `python setup_linkedin.py` |
| Create post | `Create LinkedIn post about [topic]` |
| Publish | **Automatic!** (via `execute_approved.py`) |

**Start all automations:**
```bash
# Terminal 1: Email monitoring
python gmail_watcher.py

# Terminal 2: WhatsApp monitoring  
node whatsapp_watcher_node.js

# Terminal 3: Executor (Email + WhatsApp + LinkedIn)
python execute_approved.py
```

---

## ✅ Example Workflows

### Email Example
```
1. Email received → Task in Needs Action/
2. You: "Process email messages"
3. Claude drafts response → Pending Approval/
4. You move to Approved/
5. Auto: execute_approved.py sends email! ✅
6. Auto: File moved to Done/
```

### WhatsApp Example
```
1. WhatsApp message → Task in Needs Action/
2. You: "Process WhatsApp messages"
3. Claude drafts response → Pending Approval/
4. You move to Approved/
5. Auto: execute_approved.py → Send_Queue/
6. Auto: whatsapp_watcher_node.js sends! ✅
```

### LinkedIn Example
```
1. You: "Create LinkedIn post about AI"
2. Claude creates post → Pending Approval/
3. You move to Approved/
4. Auto: execute_approved.py publishes! ✅
5. Auto: Browser opens, posts to LinkedIn
6. Auto: File moved to Done/
```

---

## 🔧 Troubleshooting

### Gmail Issues
- **Not detecting emails?** → Check `python gmail_watcher.py` is running
- **Send failed?** → Check `execute_approved.py` is running, re-authenticate if needed

### WhatsApp Issues
- **QR code not showing?** → Delete `whatsapp_session_js/`, re-scan
- **Message not sent?** → Check `whatsapp_watcher_node.js` is running
- **Session expired?** → Delete session folder, re-scan QR

### LinkedIn Issues
- **Not logged in?** → Run `python setup_linkedin.py` again
- **Post not publishing?** → Check `execute_approved.py` is running, check file in `Approved/`

---

## 📚 Detailed Skill Documentation

- **Email:** `.claude/skills/email-automation/SKILL.md`
- **WhatsApp:** `.claude/skills/whatsapp-automation/SKILL.md`
- **LinkedIn:** `.claude/skills/linkedin-automation/SKILL.md`

---

## 🎯 Best Practices

1. **Keep watchers running** - Continuous monitoring
2. **Process regularly** - Check `Needs Action/` folder
3. **Review before approving** - AI may make mistakes
4. **Monitor Dashboard.md** - See all activity
5. **Backup sessions** - `linkedin_session/`, `whatsapp_session_js/`

---

**Ready to automate? Start with your first channel!** 🚀
