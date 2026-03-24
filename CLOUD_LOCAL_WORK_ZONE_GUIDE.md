# ☁️➡️🏠 Cloud-Local Work Zone Specialization Guide
## Platinum Tier Architecture: Split Responsibilities Between Cloud and Local

**Last Updated:** March 11, 2026  
**Tier:** Platinum (Advanced Cloud-Local Hybrid)  
**Security Level:** Maximum (Credentials never leave Local)

---

## 📋 Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Cloud Responsibilities](#cloud-responsibilities)
3. [Local Responsibilities](#local-responsibilities)
4. [Communication Protocol](#communication-protocol)
5. [Vault Sync Setup](#vault-sync-setup)
6. [Security Boundaries](#security-boundaries)
7. [Workflow Examples](#workflow-examples)
8. [Troubleshooting](#troubleshooting)

---

## 🏗️ Architecture Overview

### Why Split Cloud and Local?

The Platinum Tier uses a **hybrid architecture** that maximizes the strengths of both environments:

| Aspect | Cloud (Digital Ocean) | Local (Your Laptop) |
|--------|----------------------|---------------------|
| **Availability** | 24/7 always-on | Only when you're awake |
| **Security** | Good (HTTPS, firewall) | Best (physical control) |
| **Credentials** | Limited, scoped | Full access |
| **WhatsApp** | ❌ Cannot run (needs phone) | ✅ Full session |
| **Banking** | ❌ Too risky | ✅ Secure |
| **Final Approval** | ❌ No human present | ✅ You decide |

### The Golden Rule

> **Cloud drafts, Local executes.**
> 
> Cloud never has: WhatsApp sessions, banking credentials, payment tokens, or final send authority.

---

## ☁️ Cloud Responsibilities (Digital Ocean VM)

### What Runs on Cloud

| Component | Purpose | Draft-Only Mode |
|-----------|---------|-----------------|
| **Gmail Watcher** | Monitor inbox 24/7 | ✅ Creates draft responses |
| **LinkedIn Watcher** | Create & schedule posts | ✅ Creates draft posts |
| **Odoo Community** | CRM, invoicing, accounting | ✅ Drafts require local approval |
| **Cloud Agent** | Reasoning & drafting | ✅ Cannot execute sends |
| **Dashboard** | View-only access | ✅ No approval buttons |

### Cloud Configuration

**`.env` file on Cloud:**

```bash
# Cloud Mode Settings
CLOUD_MODE=true
LOCAL_MODE=false
DRAFT_ONLY=true
REQUIRE_LOCAL_APPROVAL=true

# AI Configuration
QWEN_BASE_URL=http://localhost:11434/v1
QWEN_API_KEY=dummy-key
QWEN_MODEL=qwen2.5:latest

# Gmail API (read-only scope)
GMAIL_CREDENTIALS_PATH=/home/aivault/ai-employee-vault/credentials.json
GMAIL_TOKEN_PATH=/home/aivault/ai-employee-vault/gmail_token.json

# Odoo Configuration (draft-only)
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee_db
ODOO_USERNAME=ai@yourcompany.com
ODOO_PASSWORD=your_odoo_password

# Engine Configuration
LOG_LEVEL=INFO
POLL_INTERVAL=60
MAX_REASONING_ITERATIONS=5

# Security: Cloud cannot execute
EXECUTE_APPROVED=false
WHATSAPP_ENABLED=false
BANKING_ENABLED=false
```

### Cloud Folder Structure

```
/home/aivault/ai-employee-vault/
├── Needs_Action/           ← Cloud processes these
├── Pending_Approval/       ← Cloud creates drafts here
├── Approved/               ← Cloud moves drafts here (awaiting local sync)
├── Done/                   ← Cloud logs completed drafts
├── Updates/                ← Cloud writes updates for Local
├── Signals/                ← Cloud sends signals to Local
├── Odoo_Data/              ← Odoo data (CRM, invoices)
└── Logs/                   ← All activities logged
```

### Cloud Workflow Example

**Email arrives at 3 AM (you're sleeping):**

```
1. Gmail Watcher (Cloud) detects new email
   ↓
2. Orchestrator (Cloud) drafts response
   ↓
3. Creates: Pending_Approval/APPROVAL_send_email_20260311_030000.md
   ↓
4. Moves to: Approved/ (ready for your review)
   ↓
5. Syncs to Local via Git
   ↓
6. You wake up, review, approve locally
   ↓
7. Local executes send via Gmail API
```

---

## 🏠 Local Responsibilities (Your Laptop)

### What Runs on Local

| Component | Purpose | Execution Authority |
|-----------|---------|---------------------|
| **WhatsApp Session** | Send/receive messages | ✅ Full access |
| **Banking/Payments** | Payment operations | ✅ You control |
| **Dashboard** | Approval UI | ✅ Approve/reject buttons |
| **Execute Approved** | Final execution | ✅ Sends emails, posts |
| **Local Agent** | Review & validate | ✅ Final decision maker |

### Local Configuration

**`.env` file on Local:**

```bash
# Local Mode Settings
CLOUD_MODE=false
LOCAL_MODE=true
DRAFT_ONLY=false
EXECUTE_APPROVED=true

# AI Configuration (same as cloud)
QWEN_BASE_URL=http://localhost:11434/v1
QWEN_API_KEY=dummy-key
QWEN_MODEL=qwen2.5:latest

# Gmail API (full scope for sending)
GMAIL_CREDENTIALS_PATH=C:/Users/YourName/AI_Vault/credentials.json
GMAIL_TOKEN_PATH=C:/Users/YourName/AI_Vault/gmail_token.json

# WhatsApp Session (LOCAL ONLY!)
WHATSAPP_SESSION_PATH=C:/Users/YourName/AI_Vault/whatsapp_session
WHATSAPP_ENABLED=true

# Banking (LOCAL ONLY!)
BANKING_API_TOKEN=your_banking_token
BANKING_ENABLED=true

# Odoo Configuration (for final approval)
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee_db
ODOO_USERNAME=ai@yourcompany.com
ODOO_PASSWORD=your_odoo_password

# Engine Configuration
LOG_LEVEL=INFO
POLL_INTERVAL=30  # Faster polling when local
MAX_REASONING_ITERATIONS=5

# Security: Local has execution authority
EXECUTE_APPROVED=true
REQUIRE_HUMAN_APPROVAL=true
```

### Local Folder Structure

```
D:/DATA/HACKATHON_0/AI_Employee_Vault/
├── Needs_Action/           ← Local can also create tasks
├── Pending_Approval/       ← Synced from Cloud
├── Approved/               ← You approve these manually
├── Done/                   ← Executed tasks logged here
├── Updates/                ← Local reads cloud updates
├── Signals/                ← Local reads cloud signals
├── whatsapp_session/       ← WhatsApp Web session (NEVER syncs!)
├── credentials.json        ← Gmail OAuth (NEVER syncs!)
└── Logs/                   ← Local execution logs
```

### Local Workflow Example

**You wake up and review Cloud drafts:**

```
1. Git sync pulls Cloud updates
   ↓
2. Dashboard shows 3 pending approvals
   ↓
3. You review each approval file
   ↓
4. You move files to Approved/
   ↓
5. Execute Approved (Local) runs:
   - Sends email via Gmail API
   - Posts to LinkedIn
   - Creates Odoo lead
   ↓
6. Logs created in Done/
   ↓
7. Git sync pushes execution results to Cloud
```

---

## 🔄 Communication Protocol

### How Cloud and Local Communicate

**Primary Method: Git Sync (Recommended)**

```
Cloud (Digital Ocean)          Local (Your Laptop)
      ↓                               ↑
      └────→ Git Repository ←─────────┘
            (GitHub/GitLab)
```

**Alternative: Syncthing (Real-time)**

```
Cloud (Digital Ocean) ←────→ Local (Your Laptop)
      Direct P2P Sync
```

### File-Based Communication

**Cloud → Local Signals:**

| File Location | Purpose | Format |
|---------------|---------|--------|
| `Updates/Cloud_Status.md` | Cloud health status | Markdown |
| `Updates/New_Drafts.md` | New drafts ready | Markdown |
| `Signals/Alert_High_Priority.md` | Urgent items | Markdown |

**Local → Cloud Signals:**

| File Location | Purpose | Format |
|---------------|---------|--------|
| `Updates/Local_Acknowledgement.md` | Local received updates | Markdown |
| `Signals/Execution_Complete.md` | Task executed | Markdown |

### Signal File Format

**Cloud sends alert:**

```markdown
---
type: cloud_signal
priority: high
timestamp: 2026-03-11T03:00:00Z
signal_type: urgent_email
---

# Urgent Email Requires Attention

## Details
- **From:** important@client.com
- **Subject:** URGENT: Project Deadline
- **Received:** 2026-03-11 03:00:00 UTC

## Draft Response
Cloud has drafted a response.

## Action Required
Local agent must review and approve before sending.

---
*Generated by Cloud Agent*
```

**Local acknowledges:**

```markdown
---
type: local_signal
timestamp: 2026-03-11T09:00:00Z
signal_type: acknowledgement
references: urgent_email_20260311_030000
---

# Acknowledgement Received

## Status
- **Reviewed:** Yes
- **Approved:** Yes
- **Executed:** Yes
- **Result:** Email sent successfully at 09:15:00 UTC

---
*Local Agent Confirmation*
```

---

## 🔄 Vault Sync Setup

### Option 1: Git Sync (Recommended)

**Step 1: Setup GitHub Repository**

```bash
# On LOCAL machine
cd D:\DATA\HACKATHON_0\AI_Employee_Vault
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/ai-vault.git
git push -u origin main
```

**Step 2: Configure Cloud to Pull**

```bash
# On CLOUD server
cd /home/aivault/ai-employee-vault
git clone https://github.com/yourusername/ai-vault.git .

# Setup auto-pull script
cat > sync_from_git.sh << 'EOF'
#!/bin/bash
cd /home/aivault/ai-employee-vault

# Pull latest changes
git pull origin main

# Push cloud updates
git add Updates/ Signals/ Pending_Approval/ Approved/ Done/
git commit -m "Cloud updates: $(date)"
git push origin main

echo "Sync complete: $(date)"
EOF

chmod +x sync_from_git.sh

# Add to crontab (every 10 minutes)
(crontab -l 2>/dev/null; echo "*/10 * * * * /home/aivault/ai-employee-vault/sync_from_git.sh") | crontab -
```

**Step 3: Configure Local to Pull**

```powershell
# On LOCAL machine (PowerShell)
# Create sync script: Sync-Vault.ps1

$repoPath = "D:\DATA\HACKATHON_0\AI_Employee_Vault"
Set-Location $repoPath

# Pull latest changes
git pull origin main

# Push local updates
git add Updates/ Signals/ Done/
git commit -m "Local updates: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
git push origin main

Write-Host "Sync complete: $(Get-Date)"
```

**Step 4: Create .gitignore (CRITICAL!)**

```gitignore
# NEVER SYNC THESE - Security Risk!
.env
credentials.json
*_token.json
whatsapp_session/
linkedin_session/
gmail_token.json
*.pem
*.key

# Local-only folders
Local_Only/
Secrets/

# System files
.DS_Store
Thumbs.db
__pycache__/
*.pyc
node_modules/

# Logs (optional - can sync if you want)
# Logs/
```

### Option 2: Syncthing (Real-time Sync)

**Step 1: Install on Cloud**

```bash
# On CLOUD server
sudo apt install -y syncthing
syncthing -no-browser
# Access via: http://YOUR_DROPLET_IP:8384
```

**Step 2: Install on Local**

```powershell
# On LOCAL machine (Windows)
# Download from: https://syncthing.net/downloads/
# Install and run
```

**Step 3: Configure Sync**

1. Open Syncthing web UI on both machines
2. Add each other as devices (using Device ID)
3. Share folder: `AI_Employee_Vault`
4. Set to "Send & Receive" mode
5. **Configure ignores** (same as .gitignore above)

---

## 🔒 Security Boundaries

### What NEVER Leaves Local

| Item | Reason | Location |
|------|--------|----------|
| **WhatsApp Session** | Requires phone QR scan | Local only |
| **Gmail Credentials** | Full send authority | Local only |
| **Banking Tokens** | Financial security | Local only |
| **Payment API Keys** | Fraud prevention | Local only |
| **Private Keys** | Cryptographic security | Local only |
| **.env file** | Contains all secrets | Local only |

### Cloud Access Levels

| Resource | Cloud Access | Local Access |
|----------|--------------|--------------|
| **Gmail API** | Read-only scope | Full scope (send) |
| **Odoo** | Draft/create leads | Approve/post |
| **LinkedIn** | Draft posts | Publish posts |
| **WhatsApp** | ❌ No access | ✅ Full access |
| **Banking** | ❌ No access | ✅ Full access |
| **File System** | Vault folders only | Full system |

### Firewall Rules (Cloud)

```bash
# Allow only necessary ports
sudo ufw allow OpenSSH        # SSH access
sudo ufw allow http           # HTTP (redirect to HTTPS)
sudo ufw allow https          # HTTPS dashboard
sudo ufw allow 8069           # Odoo (local only)
sudo ufw allow 5000           # Dashboard (local only)

# Block all other incoming
sudo ufw default deny incoming

# Enable firewall
sudo ufw enable
```

---

## 📚 Workflow Examples

### Example 1: Email Response (3 AM → 9 AM)

**Timeline:**

```
03:00 AM (Cloud)
├─ Gmail Watcher detects: urgent@client.com
├─ Orchestrator drafts response
├─ Creates: Pending_Approval/APPROVAL_send_email_030000.md
├─ Moves to: Approved/
└─ Git sync pushes to GitHub

09:00 AM (Local)
├─ Git sync pulls from GitHub
├─ Dashboard shows: 1 pending approval
├─ You review and approve
├─ Execute Approved sends email
├─ Moves to: Done/
└─ Git sync pushes result to Cloud
```

**Files Created:**

```
Cloud creates:
  Approved/APPROVAL_send_email_030000.md
  
Local creates:
  Done/EXECUTED_APPROVAL_send_email_030000.md
  Updates/Email_Sent_090000.md
```

### Example 2: LinkedIn Post Scheduling

**Timeline:**

```
10:00 AM (Cloud)
├─ LinkedIn Watcher detects trend
├─ Drafts post about AI automation
├─ Creates: Pending_Approval/APPROVAL_linkedin_post_100000.md
└─ Git sync pushes

10:15 AM (Local)
├─ Git sync pulls
├─ You review post content
├─ Edit hashtags if needed
├─ Move to Approved/
└─ Execute Approved publishes

10:16 AM (Cloud)
├─ Git sync pulls execution result
├─ Logs to: Done/LINKEDIN_POST_PUBLISHED.md
└─ Updates Dashboard status
```

### Example 3: Odoo Lead Creation

**Timeline:**

```
Cloud (Anytime)
├─ Detects lead from website
├─ Creates: Pending_Approval/ODOO_LEAD_*.md
├─ Draft in Odoo CRM (status: Draft)
└─ Git sync pushes

Local (Business Hours)
├─ Git sync pulls
├─ You review lead quality
├─ Approve: Move to Approved/
├─ Execute Approved confirms in Odoo
└─ Lead status: Qualified
```

---

## 🛠️ Troubleshooting

### Issue: Cloud and Local Out of Sync

**Symptoms:**
- Local doesn't see Cloud drafts
- Cloud doesn't see Local execution

**Fix:**

```bash
# On Cloud
cd /home/aivault/ai-employee-vault
git status
git fetch origin
git reset --hard origin/main

# On Local
cd D:/DATA/HACKATHON_0/AI_Employee_Vault
git status
git fetch origin
git reset --hard origin/main
```

### Issue: Git Conflicts

**Symptoms:**
- `CONFLICT (content): Merge conflict in file.md`

**Fix:**

```bash
# On affected machine
cd /path/to/vault

# See conflicts
git status

# Edit conflicted files, resolve manually
# Then:
git add .
git commit -m "Resolved merge conflict"
git push origin main
```

### Issue: Syncthing Not Syncing

**Symptoms:**
- Files not appearing on other side
- Syncthing shows "Disconnected"

**Fix:**

1. Check both devices are online
2. Verify firewall allows port 22000
3. Re-add device using Device ID
4. Check folder permissions

### Issue: Cloud Cannot Access Odoo

**Symptoms:**
- Odoo connection timeout
- Lead creation fails

**Fix:**

```bash
# On Cloud
docker-compose -f docker-compose-odoo.yml ps
docker-compose -f docker-compose-odoo.yml restart
docker-compose -f docker-compose-odoo.yml logs web
```

---

## ✅ Work Zone Checklist

### Cloud Setup Complete When:

- [ ] Droplet running on Digital Ocean
- [ ] All Python/Node dependencies installed
- [ ] Odoo running via Docker
- [ ] PM2 managing all processes
- [ ] `.env` configured with `CLOUD_MODE=true`
- [ ] Gmail API authenticated (read-only)
- [ ] Git sync working (pull/push)
- [ ] Firewall configured (UFW)
- [ ] Health checks running
- [ ] **WhatsApp session NOT present** ✅
- [ ] **Banking credentials NOT present** ✅

### Local Setup Complete When:

- [ ] Project cloned locally
- [ ] All dependencies installed
- [ ] `.env` configured with `LOCAL_MODE=true`
- [ ] WhatsApp session authenticated
- [ ] Gmail API authenticated (full scope)
- [ ] Dashboard running on localhost:5000
- [ ] Execute Approved running
- [ ] Git sync working
- [ ] **Cloud credentials secured** ✅
- [ ] **Approval workflow tested** ✅

---

## 📊 Performance Metrics

### Expected Latency

| Operation | Cloud → Local | Local → Cloud |
|-----------|---------------|---------------|
| **Git Sync** | 10 minutes | 10 minutes |
| **Syncthing** | < 1 minute | < 1 minute |
| **Urgent Alert** | Immediate (email) | Immediate (email) |

### Availability

| Component | Cloud Uptime | Local Uptime |
|-----------|--------------|--------------|
| **Gmail Watcher** | 99.9% (24/7) | When laptop on |
| **LinkedIn** | 99.9% (24/7) | When laptop on |
| **Odoo** | 99.9% (24/7) | When laptop on |
| **WhatsApp** | N/A | When laptop on |
| **Approval UI** | N/A | When laptop on |

---

## 🎯 Summary

### Cloud (Digital Ocean) Does:

✅ 24/7 monitoring (Gmail, LinkedIn)  
✅ Draft responses and posts  
✅ Odoo CRM draft creation  
✅ Health monitoring  
✅ Git sync coordination  
❌ NO WhatsApp  
❌ NO Banking  
❌ NO final execution  

### Local (Your Laptop) Does:

✅ Human approval & review  
✅ WhatsApp messaging  
✅ Banking/payments  
✅ Final execution (send/post)  
✅ Dashboard UI  
✅ Cloud sync coordination  

---

**You now have a production-ready, secure, hybrid AI Employee system! 🎉**

*Cloud works while you sleep. Local approves while you're awake. Perfect partnership!*
