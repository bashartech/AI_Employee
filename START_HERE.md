# AI Employee Vault - Quick Start Guide

## Complete Automation Flow

Your AI Employee system has 3 main components that work together:

### 1. Watchers (Create Tasks)
These monitor external sources and create task files in `Needs Action/` folder:

```bash
# Start Gmail watcher
python gmail_watcher.py

# Start WhatsApp watcher
node whatsapp_watcher_node.js

# Start LinkedIn watcher
python linkedin_watcher.py
```

**What they do:** Monitor Gmail, WhatsApp, LinkedIn → Create task files in `Needs Action/`

---

### 2. Orchestrator (Process Tasks with Claude)
This watches `Needs Action/` folder and processes tasks with Claude Code:

```bash
# Start the orchestrator
python run_automation.py

# OR use batch file
run_orchestrator.bat
```

**What it does:**
- Watches `Needs Action/` folder
- When new task appears → Invokes Claude Code
- Claude reads task → Drafts response → Creates approval file in `Pending Approval/`

---

### 3. Executor (Execute Approved Actions)
This watches `Approved/` folder and executes approved actions:

```bash
# Start the executor
python execute_approved.py

# OR use batch file
run_executor.bat
```

**What it does:**
- Watches `Approved/` folder
- When you move approval file there → Executes the action
- Sends email / WhatsApp / LinkedIn post
- Moves completed files to `Done/`

---

## Complete Workflow Example

### Email Automation Flow:

1. **New email arrives** → `gmail_watcher.py` creates `EMAIL_xxx.md` in `Needs Action/`

2. **Orchestrator detects it** → Invokes Claude Code → Claude drafts response → Creates `APPROVAL_send_email_xxx.md` in `Pending Approval/`

3. **You review** → Open `Pending Approval/APPROVAL_send_email_xxx.md` → Edit if needed → Move to `Approved/`

4. **Executor detects it** → Sends email via `send_email.js` → Moves to `Done/`

---

## Quick Start (All 3 Components)

Open 3 terminals:

**Terminal 1 - Watchers:**
```bash
python gmail_watcher.py
```

**Terminal 2 - Orchestrator:**
```bash
python run_automation.py
```

**Terminal 3 - Executor:**
```bash
python execute_approved.py
```

Now the complete automation is running! 🎉

---

## Folder Structure

```
Needs Action/       ← Watchers create tasks here
    ↓
Pending Approval/   ← Claude creates approval files here
    ↓ (You review and move to Approved)
Approved/           ← You move approved files here
    ↓
Done/               ← Executor moves completed files here
```

---

## Troubleshooting

**Tasks stuck in Needs Action?**
- Make sure `run_automation.py` (orchestrator) is running
- Check logs for errors

**Approval files not being executed?**
- Make sure `execute_approved.py` (executor) is running
- Verify approval file format matches skill requirements

**No tasks being created?**
- Make sure watchers are running
- Check watcher logs for authentication issues

---

## Important Notes

- **Orchestrator** uses Claude Code (you!) to process tasks intelligently
- **Executor** handles the actual sending (email, WhatsApp, LinkedIn)
- **You** review and approve all actions before they're executed
- All 3 components should be running for full automation

---

## Next Steps

1. Start all 3 components (watchers, orchestrator, executor)
2. Send yourself a test email
3. Watch it flow through the system
4. Review and approve the drafted response
5. See it get sent automatically!

🚀 Your AI Employee is now working for you!
