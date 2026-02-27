# 🤖 Claude Code Automation Setup Guide

## Complete Automation for AI Employee Vault

This guide will help you set up **fully automatic** task processing with Claude Code.

---

## 📋 **What You'll Get**

✅ **Automatic Task Processing** - No manual prompting needed  
✅ **Smart Approval System** - Claude decides what needs human review  
✅ **Ralph Wiggum Loop** - Auto-retry until task complete  
✅ **Skill-Based Processing** - Follows `.claude/skills/` files  
✅ **Complete Audit Trail** - All actions logged  

---

## 🚀 **Quick Start (10 minutes)**

### **Step 1: Install Claude Code**

**Option A: Claude Code (Paid)**
```bash
npm install -g @anthropic-ai/claude-code
claude login
```

**Option B: Claude Code Router (Free with Gemini API)**
```bash
# Download from: https://github.com/jasonharris/claude-code-router
# Follow setup instructions
```

### **Step 2: Verify Installation**
```bash
claude --version
```

Should show: `Claude Code X.X.X`

### **Step 3: Test Connection**
```bash
claude --prompt "Hello" --working-directory "D:\DATA\HACKATHON_0\AI_Employee_Vault"
```

### **Step 4: Start Automation**

**Double-click:**
```
run_claude_automation.bat
```

**Or run manually:**
```bash
python claude_orchestrator.py
```

---

## 📊 **How It Works**

### **Automatic Workflow**

```
┌─────────────────────────────────────────────────────────────┐
│  1. WATCHERS (Always Running)                               │
│  - gmail_watcher.py          → Creates EMAIL_*.md          │
│  - whatsapp_watcher_node.js  → Creates WHATSAPP_*.md       │
│  - linkedin_watcher.py       → Creates LINKEDIN_*.md       │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  2. CLAUDE ORCHESTRATOR (Auto-Detects)                      │
│  - Detects new file in Needs Action/                        │
│  - Reads .claude/skills/ for instructions                   │
│  - Processes task automatically                             │
│  - Creates approval files if needed                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  3. HUMAN APPROVAL (You Review)                             │
│  - Notification: "Approval needed"                          │
│  - Review file in Pending Approval/                         │
│  - Move to Approved/ to approve                            │
│  - Move to Rejected/ to reject                             │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  4. EXECUTOR (Always Running)                               │
│  - Detects file in Approved/                                │
│  - Executes action (email/WhatsApp/LinkedIn/Odoo)           │
│  - Moves to Done/                                           │
│  - Logs to audit                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 **Folder Structure**

```
AI_Employee_Vault/
├── .claude/
│   ├── settings.json          ← Claude Code configuration
│   └── skills/
│       ├── email-automation/  ← Email processing skill
│       ├── whatsapp-automation/ ← WhatsApp processing skill
│       ├── linkedin-automation/ ← LinkedIn processing skill
│       └── odoo/              ← Odoo CRM/Invoice skill
├── Needs Action/              ← New tasks appear here
├── Pending Approval/          ← Awaiting your approval
├── Approved/                  ← Move approved tasks here
├── Done/                      ← Completed tasks
├── Rejected/                  ← Rejected tasks
├── claude_orchestrator.py     ← Main automation script
├── run_claude_automation.bat  ← Easy launcher
└── execute_approved.py        ← Executes approved actions
```

---

## 🎯 **Task Types & Processing**

### **Email Tasks**
**File:** `EMAIL_*.md` or contains "email"

**Claude Code will:**
1. Read email from `Needs Action/`
2. Draft professional response
3. Create `Pending Approval/APPROVAL_send_email_*.md`
4. Wait for your approval

**You:** Review → Move to `Approved/`

**Executor:** Sends email via Gmail API

---

### **WhatsApp Tasks**
**File:** `WHATSAPP_*.md` or contains "whatsapp"

**Claude Code will:**
1. Read message from `Needs Action/`
2. Draft response
3. Create `Pending Approval/APPROVAL_send_whatsapp_*.md`
4. Wait for your approval

**You:** Review → Move to `Approved/`

**Executor:** Sends via WhatsApp

---

### **LinkedIn Post Tasks**
**File:** `LINKEDIN_POST_*.md` or contains "linkedin post"

**Claude Code will:**
1. Read post request from `Needs Action/`
2. Create professional post with hashtags
3. Create `Pending Approval/APPROVAL_linkedin_post_*.md`
4. Wait for your approval

**You:** Review → Move to `Approved/`

**Executor:** Posts to LinkedIn

---

### **LinkedIn Lead Tasks**
**File:** `LINKEDIN_COMMENT_*.md` or `LINKEDIN_MESSAGE_*.md`

**Claude Code will:**
1. Read lead from `Needs Action/`
2. Analyze interest level
3. Create lead approval file
4. Wait for your approval

**You:** Review → Move to `Approved/`

**Executor:** Creates lead in Odoo CRM

---

### **Odoo Tasks**
**File:** `ODOO_LEAD_*.md`, `ODOO_INV_*.md`, `ODOO_QUO_*.md`

**Claude Code will:**
1. Read details from `Needs Action/`
2. Extract required fields
3. Create approval file
4. Wait for your approval

**You:** Review → Move to `Approved/`

**Executor:** Creates in Odoo

---

## ⚙️ **Configuration**

### **Edit `.claude/settings.json`**

```json
{
  "model": "claude-sonnet-4-20250514",
  "max_tokens": 8192,
  "temperature": 0.7,
  "workflow": {
    "check_interval_seconds": 60,
    "max_iterations": 10,
    "approval_required_for": [
      "send_email",
      "send_whatsapp",
      "post_linkedin",
      "create_invoice",
      "create_quotation"
    ]
  }
}
```

**Customize:**
- `check_interval_seconds`: How often to check for new tasks (default: 60)
- `max_iterations`: Max retry attempts per task (default: 10)
- `approval_required_for`: Actions that always need approval

---

## 🔧 **Troubleshooting**

### **Claude Code not found**
```bash
# Check installation
where claude

# Reinstall if needed
npm install -g @anthropic-ai/claude-code
```

### **Authentication error**
```bash
# Login to Claude Code
claude login
```

### **Tasks not being processed**
1. Check orchestrator is running: `python claude_orchestrator.py`
2. Verify file is in `Needs Action/` folder
3. Check file extension is `.md` or `.txt`
4. Review console output for errors

### **Approval files not created**
1. Check `.claude/skills/` folder exists
2. Verify skill files are present
3. Check Claude Code has read access to vault

### **Executor not processing approvals**
1. Check executor is running: `python execute_approved.py`
2. Verify file is in `Approved/` folder
3. Check filename matches pattern (e.g., `APPROVAL_send_email_*.md`)

---

## 📊 **Status Commands**

**Check orchestrator status:**
```bash
python claude_orchestrator.py
# Shows: Needs Action, Pending Approval, Approved, Done counts
```

**Check executor status:**
```bash
python execute_approved.py
# Shows: Monitoring status and processed files
```

**View audit log:**
```bash
type Logs\audit_2026-02-24.log
```

---

## 🎓 **Best Practices**

### **For Safe Automation:**
✅ Keep human approval for sensitive actions (email, payments, posts)  
✅ Review approval files before approving  
✅ Check audit logs regularly  
✅ Test with dummy tasks first  

### **For Efficiency:**
✅ Run orchestrator and executor as background services  
✅ Set up Windows Task Scheduler for auto-start  
✅ Use batch files for easy launching  
✅ Monitor disk space for logs  

### **For Security:**
✅ Never commit `.env` or credentials  
✅ Keep `linkedin_session/` and `whatsapp_session/` private  
✅ Review audit logs for unusual activity  
✅ Use separate Odoo user for AI with limited permissions  

---

## 🚀 **Advanced: Windows Task Scheduler**

### **Auto-Start on Boot**

1. Open **Task Scheduler**
2. Create Basic Task: "AI Employee Orchestrator"
3. Trigger: "When the computer starts"
4. Action: "Start a program"
5. Program: `D:\DATA\HACKATHON_0\AI_Employee_Vault\run_claude_automation.bat`
6. Start in: `D:\DATA\HACKATHON_0\AI_Employee_Vault`

Repeat for `run_executor.bat` to start executor automatically.

---

## 📈 **Next Steps**

1. ✅ **Test Setup:**
   ```bash
   claude --version
   python claude_orchestrator.py
   ```

2. ✅ **Create Test Task:**
   - Create file: `Needs Action/test_task.md`
   - Content: "Analyze this: Q1 sales were $50,000"
   - Watch Claude Code process it automatically

3. ✅ **Monitor First Run:**
   - Watch console output
   - Check `Pending Approval/` for approval files
   - Review `Done/` for completed tasks

4. ✅ **Start Full Automation:**
   ```bash
   # Terminal 1
   python claude_orchestrator.py
   
   # Terminal 2
   python execute_approved.py
   ```

---

## 🎉 **You're Done!**

Your AI Employee is now **fully automatic** with Claude Code!

**What happens now:**
- Watchers detect emails/messages/leads
- Claude Code processes them automatically
- You only review approvals
- Executor handles the rest

**Sit back and let your AI Employee work!** 🤖✨

---

**Need Help?**
- Check `prompt.md` for architecture details
- Review `.claude/skills/` for processing instructions
- Read audit logs in `Logs/` folder
