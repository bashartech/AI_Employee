# AI Employee Vault - Quick Reference Guide

## 🚀 Quick Start Commands

### Start All Services
```bash
# Windows
start_all.bat

# Linux/Mac
chmod +x start_all.sh
./start_all.sh
```

### Stop All Services
```bash
# Windows
stop_all.bat

# Linux/Mac
chmod +x stop_all.sh
./stop_all.sh
```

### Start Individual Components
```bash
# Orchestrator (processes tasks)
python engine/orchestrator.py

# Execute Approved (sends emails, creates leads)
python execute_approved.py

# Dashboard (monitoring interface)
cd dashboard && python app.py

# Gmail Watcher (monitors inbox)
python gmail_watcher.py

# WhatsApp Watcher (monitors messages)
node whatsapp_watcher_node.js
```

### Start Odoo
```bash
# Start container
docker start oddo

# Check status
docker ps | grep oddo

# View logs
docker logs -f oddo
```

---

## 📁 Folder Workflow

### 1. Create Task
Drop file in `Inbox/` or `Needs Action/`

### 2. Orchestrator Processes
- Detects task type (email, whatsapp, linkedin, odoo)
- Drafts response/action
- Creates approval file in `Pending Approval/`

### 3. Human Reviews
- Open `Pending Approval/` folder
- Review drafted response
- Move to `Approved/` (to execute) or `Rejected/` (to cancel)

### 4. Execute Approved Runs
- Detects approved file
- Executes action (send email, create lead, etc.)
- Moves to `Done/` with execution log

---

## 📧 Email Task Examples

### Gmail Smart Filtering (NEW!)

**Automatic Filtering:**
- ✅ Only important emails reach Needs Action
- ❌ Promotional emails automatically blocked
- ❌ Social media notifications filtered
- ❌ Receipts/updates filtered

**Customize Filtering:**
```bash
# Edit configuration
notepad gmail_filter_config.py

# Adjust strictness (1-10, default: 5)
MIN_IMPORTANCE_SCORE = 5

# Add VIP senders
WHITELIST_DOMAINS = ['@client.com', 'boss@company.com']

# Block senders
BLACKLIST_DOMAINS = ['noreply@', '@spammer.com']
```

**View Statistics:**
```
[10:30:15] Found 3 important email(s)
  ✓ Important: Important email (score: 8)
  ✗ Filtered: Promotional email (Gmail category)
  ✓ Important: Important email (score: 7)

📊 Statistics:
  Processed: 2
  Filtered: 1
  Filter Rate: 33.3%
```

See `GMAIL_FILTERING_GUIDE.md` for complete guide.

### Simple Email
**File:** `Needs Action/email_client.md`
```markdown
Send email to john@example.com

Subject: Meeting Confirmation
Body: Confirming our meeting tomorrow at 2 PM.
```

### Inbox Email (Auto-detected)
**File:** `Inbox/email_inquiry.md`
```markdown
---
source: inbox
---

## From
customer@company.com

## Subject
Product Inquiry

## Content
What are your pricing options for enterprise?
```

---

## 💬 WhatsApp Task Examples

### Simple WhatsApp
**File:** `Needs Action/whatsapp_client.md`
```markdown
Send WhatsApp to +1234567890

Message: Thanks for your order! We'll ship it tomorrow.
```

### Inbox WhatsApp
**File:** `Inbox/whatsapp_inquiry.md`
```markdown
---
source: inbox
---

## From
+9876543210

## Content
Do you have this product in stock?
```

---

## 🏢 Odoo Lead Examples

### Create Lead
**File:** `Needs Action/new_lead.md`
```markdown
create new lead in odoo
name: Sarah Johnson
email: sarah@company.com
phone: +1234567890
age: 28
course: Digital Marketing
```

### From Inbox
**File:** `Inbox/lead_inquiry.md`
```markdown
---
source: inbox
---

## Content
create lead in odoo
name: Mike Chen
email: mike@startup.com
phone: +9876543210
course: Web Development
```

**Keywords detected:** lead, crm, odoo, oddo, create lead, new lead

---

## 🔗 LinkedIn Post Examples

### Create Post
**File:** `Needs Action/linkedin_post.md`
```markdown
Create LinkedIn post about our new product launch

Content:
🚀 Excited to announce our new AI automation platform!

Key features:
✅ Email automation
✅ CRM integration
✅ Real-time analytics

Learn more: https://example.com

#AI #Automation #ProductLaunch
```

---

## 📊 Dashboard Access

### URLs
- **Dashboard:** http://localhost:5000
- **Odoo CRM:** http://localhost:8069

### Dashboard Features
- Real-time task counts
- System resource monitoring (CPU, Memory, Disk)
- Activity timeline chart (24 hours)
- Task distribution chart (by type)
- Watcher status indicators
- Live activity feed
- Task management (view, approve, reject)

### Dashboard Shortcuts
- **Esc** - Close modal
- **Ctrl+R** - Refresh page
- **F12** - Open developer tools

---

## 🔧 Troubleshooting Quick Fixes

### Orchestrator Not Processing
```bash
# Check if running
ps aux | grep orchestrator  # Linux/Mac
tasklist | findstr python   # Windows

# Restart
python engine/orchestrator.py
```

### Execute Approved Not Working
```bash
# Check file naming
ls "Pending Approval/"

# Should be:
# APPROVAL_send_email_*.md
# APPROVAL_send_whatsapp_*.md
# ODOO_LEAD_*.md
# LINKEDIN_POST_*.md

# Restart
python execute_approved.py
```

### Dashboard Not Loading
```bash
# Check port
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # Linux/Mac

# Restart
cd dashboard && python app.py
```

### Odoo Connection Failed
```bash
# Start Odoo
docker start oddo

# Check credentials in mcp_servers/odoo_server.py
# Verify: url, db, username, password
```

### WhatsApp Not Sending
```bash
# Re-authenticate
rm -rf whatsapp_session_js/
node whatsapp_watcher_node.js
# Scan new QR code
```

### Gmail API Errors
```bash
# Re-authenticate
rm gmail_token.json
python gmail_watcher.py
# Follow OAuth flow
```

---

## 📝 File Naming Conventions

### Task Files (Input)
- `task_name.md` - Any descriptive name
- `INBOX_*.md` - From inbox watcher
- Use `.md` or `.txt` extension

### Approval Files (Generated)
- `APPROVAL_send_email_TIMESTAMP.md` - Email approval
- `APPROVAL_send_whatsapp_TIMESTAMP.md` - WhatsApp approval
- `ODOO_LEAD_Name_TIMESTAMP.md` - Odoo lead approval
- `LINKEDIN_POST_TIMESTAMP.md` - LinkedIn post approval

### Execution Logs (Output)
- `EXECUTED_*.md` - Execution log in Done/
- Contains original approval + execution result

---

## 🎯 Task Type Detection

### Email Tasks
**Keywords:** email, send email, write email
**Patterns:** email addresses (user@domain.com)

### WhatsApp Tasks
**Keywords:** whatsapp, watsapp, send whatsapp
**Patterns:** phone numbers (+1234567890)

### LinkedIn Tasks
**Keywords:** linkedin, post, social media, share

### Odoo Tasks
**Keywords:** odoo, oddo, lead, crm, create lead, new lead, invoice, quotation
**Patterns:** name:, email:, phone:, course:

---

## 🔐 Security Checklist

- [ ] Never commit credentials to git
- [ ] Use .env for sensitive data
- [ ] Review all approvals before moving to Approved/
- [ ] Enable 2FA on Gmail, LinkedIn, Odoo
- [ ] Regularly check audit logs
- [ ] Use HTTPS in production
- [ ] Limit API permissions to minimum required

---

## 📈 Performance Tips

1. **Reduce polling frequency** - Edit watcher intervals
2. **Limit log retention** - Rotate logs weekly
3. **Use background mode** - Run as system services
4. **Enable caching** - Dashboard caches data
5. **Monitor resources** - Check dashboard metrics

---

## 🆘 Emergency Commands

### Kill All Processes
```bash
# Windows
taskkill /F /IM python.exe
taskkill /F /IM node.exe

# Linux/Mac
pkill -9 python
pkill -9 node
```

### Clear All Tasks (CAUTION)
```bash
# Backup first!
cp -r "Needs Action" "Needs Action.backup"
cp -r "Pending Approval" "Pending Approval.backup"

# Then clear
rm "Needs Action"/*.md
rm "Pending Approval"/*.md
```

### Reset WhatsApp Session
```bash
rm -rf whatsapp_session_js/
node whatsapp_watcher_node.js
# Scan new QR code
```

### Reset Gmail Token
```bash
rm gmail_token.json
python gmail_watcher.py
# Complete OAuth flow
```

---

## 📞 Support Resources

1. **README.md** - Complete documentation
2. **SKILL.md** - Detailed workflows
3. **dashboard/README.md** - Dashboard guide
4. **Browser Console** - F12 for errors
5. **Logs folder** - Check logs/*.log files

---

## ✅ Daily Checklist

### Morning
- [ ] Start all services (`start_all.bat`)
- [ ] Check dashboard (http://localhost:5000)
- [ ] Verify all watchers are online
- [ ] Review pending approvals

### During Day
- [ ] Monitor dashboard for new tasks
- [ ] Review and approve pending tasks
- [ ] Check activity feed for errors

### Evening
- [ ] Review completed tasks in Done/
- [ ] Check logs for any errors
- [ ] Backup important data
- [ ] Stop services if not running 24/7 (`stop_all.bat`)

---

**Quick Help:** Press F12 in dashboard to see console logs for debugging.

**Need Help?** Check README.md or review logs in logs/ folder.
