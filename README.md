# 🤖 AI Employee Vault - Complete Automation System

**Autonomous task management system with Email, WhatsApp, LinkedIn, and Odoo CRM integration**

[![Claude Code](https://img.shields.io/badge/Claude-Code-blue)](https://claude.ai)
[![Python](https://img.shields.io/badge/Python-3.8+-green)](https://python.org)
[![Node.js](https://img.shields.io/badge/Node.js-18+-brightgreen)](https://nodejs.org)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 🎯 Overview

AI Employee Vault is a complete automation system that monitors your communications (Gmail, WhatsApp, LinkedIn) and business operations (Odoo CRM), drafts intelligent responses using Claude AI, and executes approved actions automatically.

### Key Features

✅ **Email Automation** - Monitor Gmail, draft responses, send approved emails
✅ **WhatsApp Automation** - Monitor messages, auto-reply, send approved messages
✅ **LinkedIn Automation** - Create and publish posts with approval workflow
✅ **Odoo CRM Integration** - Create leads, invoices, and quotations automatically
✅ **Professional Dashboard** - Real-time monitoring with charts and analytics
✅ **Human-in-the-Loop** - Approval workflow for sensitive actions
✅ **Complete Audit Trail** - All actions logged with timestamps
✅ **Responsive Design** - Works on desktop, tablet, and mobile

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    INBOX (File Drop)                        │
│              Drop tasks manually or via watchers            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   NEEDS ACTION                              │
│         Orchestrator monitors and processes tasks           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 PENDING APPROVAL                            │
│        AI-drafted responses await human review              │
└────────────────────────┬────────────────────────────────────┘
                         │
                    Human Reviews
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                     APPROVED                                │
│         Execute Approved watcher sends/creates              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                       DONE                                  │
│              Completed tasks with logs                      │
└─────────────────────────────────────────────────────────────┘
```

### Components

1. **Watchers** - Monitor Gmail, WhatsApp, LinkedIn for new messages
2. **Orchestrator** - Processes tasks from Needs Action folder
3. **Execute Approved** - Executes approved actions (send emails, create leads)
4. **Dashboard** - Real-time monitoring and task management
5. **Inbox** - Manual task drop zone

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- Docker (for Odoo)
- Gmail API credentials
- Claude Code CLI

### Step 1: Install Dependencies

**Python:**
```bash
pip install -r requirements.txt
```

**Node.js:**
```bash
npm install
```

### Step 2: Configure Credentials

**Gmail API:**
1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create project and enable Gmail API
3. Download `credentials.json` to project root
4. Run `python gmail_watcher.py` once to authenticate

**WhatsApp:**
- First run will generate QR code for authentication
- Scan with WhatsApp mobile app

**LinkedIn:**
- Configure session in `linkedin_session` file

**Odoo:**
```bash
# Start Odoo container
docker start oddo

# Or use docker-compose
docker-compose -f docker-compose-odoo.yml up -d
```

Update `mcp_servers/odoo_server.py` with your Odoo credentials.

### Step 3: Start All Components

**Terminal 1 - Orchestrator:**
```bash
python engine/orchestrator.py
```

**Terminal 2 - Execute Approved:**
```bash
python execute_approved.py
```

**Terminal 3 - Dashboard:**
```bash
cd dashboard
python app.py
```

**Terminal 4 - Gmail Watcher (optional):**
```bash
python gmail_watcher.py
```

**Terminal 5 - WhatsApp Watcher (optional):**
```bash
node whatsapp_watcher_node.js
```

**Access Dashboard:**
```
http://localhost:5000
```

---

## 📊 Dashboard Features

### Professional Monitoring Interface

- **Real-time System Metrics** - CPU, Memory, Disk usage
- **Interactive Charts** - Activity timeline and task distribution
- **Live Activity Feed** - Recent system activities
- **Watcher Status** - Online/offline indicators for all watchers
- **Task Management** - View, approve, reject tasks from dashboard
- **Analytics** - Hourly and daily task completion stats
- **Responsive Design** - Works on all devices (desktop, tablet, mobile)

### Dashboard Sections

**Left Sidebar:**
- Autonomy level indicator
- Memory banks (task counts)
- Workflow pipeline visualization
- Active skills progress bars
- System resource monitoring

**Center Panel:**
- Quick stats cards (today's tasks, success rate, weekly stats)
- Activity chart (24-hour timeline)
- Distribution chart (task breakdown by type)
- Task lists with tabs (Pending, Needs Action, Approved, Done)

**Right Sidebar:**
- Watcher status (WhatsApp, Gmail, LinkedIn, Orchestrator)
- Live activity feed
- Quick actions (refresh, download logs, settings)

---

## 📧 Email Automation

### How It Works

1. **Gmail Watcher** monitors inbox for new emails
2. Creates task file in `Needs Action/`
3. **Orchestrator** detects email task and drafts response
4. Response moved to `Pending Approval/`
5. You review and approve
6. **Execute Approved** sends email via Gmail API

### 🎯 Smart Email Filtering (NEW!)

The Gmail watcher now includes **intelligent filtering** that automatically blocks 70-90% of unwanted emails:

**Automatically Filtered:**
- ❌ Promotional emails (ads, sales, discounts)
- ❌ Social media notifications
- ❌ Receipts and updates
- ❌ Forum/mailing list emails
- ❌ Newsletter spam

**Always Processed:**
- ✅ Primary inbox emails
- ✅ Gmail "Important" marked emails
- ✅ Professional/work-related emails
- ✅ Whitelisted senders

**Configuration:**

Edit `gmail_filter_config.py` to customize:

```python
# Adjust strictness (1-10, default: 5)
MIN_IMPORTANCE_SCORE = 5

# Add VIP senders (always pass through)
WHITELIST_DOMAINS = [
    '@importantclient.com',
    'boss@company.com',
]

# Block specific senders
BLACKLIST_DOMAINS = [
    'noreply@',
    '@spammer.com',
]
```

**Benefits:**
- 70-90% noise reduction
- Only important emails reach Needs Action
- Saves time and API costs
- Fully customizable

See `GMAIL_FILTERING_GUIDE.md` for complete documentation.

### Usage

**Manual Email Task:**

Create `Needs Action/email_task.md`:
```markdown
Send email to client@example.com about project update

Subject: Project Status Update
Body: Provide update on Q1 deliverables
```

**Inbox Email:**

Drop file in `Inbox/`:
```markdown
---
source: inbox
type: email
---

## From
client@example.com

## Subject
Question about pricing

## Content
What are your rates for consulting?
```

---

## 💬 WhatsApp Automation

### How It Works

1. **WhatsApp Watcher** monitors WhatsApp Web for messages
2. Creates task file in `Needs Action/`
3. **Orchestrator** drafts response
4. Response moved to `Pending Approval/`
5. You review and approve
6. **Execute Approved** adds to Send_Queue
7. **WhatsApp Watcher** sends message automatically

### Usage

**Manual WhatsApp Task:**

Create `Needs Action/whatsapp_task.md`:
```markdown
Send WhatsApp to +1234567890

Message: Thanks for your inquiry. Our team will contact you soon.
```

---

## 🔗 LinkedIn Automation

### How It Works

1. Draft post content
2. **Orchestrator** creates approval file
3. You review and approve
4. **Execute Approved** publishes to LinkedIn

### Usage

Create `Needs Action/linkedin_post.md`:
```markdown
Create LinkedIn post about AI automation

Content:
🤖 Excited to share our new AI automation system!

Key features:
- Email automation
- WhatsApp integration
- CRM synchronization

#AI #Automation #Productivity
```

---

## 🏢 Odoo CRM Integration

### Features

- **Lead Creation** - Automatically create CRM leads
- **Invoice Generation** - Create invoices for customers
- **Quotation Management** - Generate sales quotations

### How It Works

1. Drop lead creation task in `Inbox/` or `Needs Action/`
2. **Orchestrator** detects Odoo task (keywords: lead, crm, odoo, oddo)
3. Creates `ODOO_LEAD_*.md` approval file
4. You review and approve
5. **Execute Approved** creates lead in Odoo CRM
6. Lead saved to `Odoo_Data/Leads/`

### Usage

**Create Lead:**

Create `Needs Action/new_lead.md`:
```markdown
create new lead in odoo with this data
name: John Smith
age: 25
course: Computer Science
email: john@example.com
phone: +1234567890
```

**From Inbox:**

Drop in `Inbox/`:
```markdown
---
source: inbox
---

## Content

create new lead in odoo
name: Sarah Johnson
email: sarah@company.com
phone: +9876543210
course: Data Analytics
```

**Approval File Format:**

The orchestrator creates:
```markdown
---
type: odoo_approval
action: create_lead
lead_name: John Smith
email: john@example.com
phone: +1234567890
source: Inbox
---

# Odoo Lead Creation Approval

## Lead Information
**Name:** John Smith
**Email:** john@example.com
**Phone:** +1234567890
**Source:** Inbox

## Instructions
1. Review the lead information
2. Edit if needed (update YAML fields)
3. Move to Approved/ to create in Odoo
4. Move to Rejected/ to cancel
```

### Odoo Setup

**Start Odoo:**
```bash
docker start oddo
```

**Access Odoo:**
```
http://localhost:8069
```

**Configure:**
Update credentials in `mcp_servers/odoo_server.py`:
```python
self.url = "http://localhost:8069"
self.db = "your_database"
self.username = "your_email@example.com"
self.password = "your_password"
```

---

## 📁 Folder Structure

```
AI_Employee_Vault/
├── Inbox/                  # Manual task drop zone
│   └── Processed/          # Processed inbox tasks
├── Needs Action/           # Tasks awaiting processing
├── Pending Approval/       # AI-drafted responses for review
├── Approved/               # Approved tasks ready for execution
├── Done/                   # Completed tasks with logs
├── Rejected/               # Rejected tasks
├── Send_Queue/             # WhatsApp messages queued to send
├── Odoo_Data/              # Odoo CRM data
│   └── Leads/              # Created leads
├── dashboard/              # Flask dashboard
│   ├── app.py              # Dashboard server
│   ├── templates/          # HTML templates
│   └── static/             # CSS, JS, assets
├── engine/                 # Core automation engine
│   ├── orchestrator.py     # Main task processor
│   ├── logger.py           # Logging system
│   └── linkedin_poster.py  # LinkedIn integration
├── mcp_servers/            # Integration servers
│   └── odoo_server.py      # Odoo CRM integration
├── .claude/                # Claude Code configuration
├── gmail_watcher.py        # Gmail monitoring
├── whatsapp_watcher_node.js # WhatsApp monitoring
├── execute_approved.py     # Approved action executor
├── send_email.js           # Email sender
└── requirements.txt        # Python dependencies
```

---

## 🎛️ Configuration

### Environment Variables

Create `.env` file:
```bash
# Gmail API
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=gmail_token.json

# Odoo
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee_db
ODOO_USERNAME=your_email@example.com
ODOO_PASSWORD=your_password

# Dashboard
DASHBOARD_PORT=5000
```

### Dashboard Customization

**Change refresh intervals** in `dashboard/static/js/dashboard.js`:
```javascript
// Dashboard refresh (default: 30 seconds)
refreshInterval = setInterval(refreshDashboard, 30000);

// Activity feed (default: 10 seconds)
activityInterval = setInterval(loadRecentActivity, 10000);

// System metrics (default: 5 seconds)
systemMetricsInterval = setInterval(loadSystemMetrics, 5000);
```

**Change port** in `dashboard/app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=8080)
```

---

## 🔧 Troubleshooting

### Orchestrator Not Processing Tasks

**Check if running:**
```bash
ps aux | grep orchestrator
```

**View logs:**
```bash
tail -f logs/orchestrator.log
```

**Restart:**
```bash
python engine/orchestrator.py
```

### Execute Approved Not Detecting Files

**Check file naming:**
- Email: `APPROVAL_send_email_*.md`
- WhatsApp: `APPROVAL_send_whatsapp_*.md`
- LinkedIn: `LINKEDIN_POST_*.md`
- Odoo: `ODOO_LEAD_*.md`

**Verify watcher is running:**
```bash
ps aux | grep execute_approved
```

### Dashboard Not Loading

**Check Flask is running:**
```bash
netstat -ano | findstr :5000
```

**Clear browser cache:**
```
Ctrl+Shift+Delete
```

**Reinstall dependencies:**
```bash
pip install -r requirements.txt --force-reinstall
```

### Odoo Connection Failed

**Start Odoo container:**
```bash
docker start oddo
docker ps | grep oddo
```

**Check credentials:**
- Verify URL, database name, username, password in `mcp_servers/odoo_server.py`

**Test connection:**
```bash
python test_odoo.py
```

### WhatsApp Not Sending

**Check session:**
```bash
ls -la whatsapp_session_js/
```

**Re-authenticate:**
- Delete `whatsapp_session_js/` folder
- Restart `whatsapp_watcher_node.js`
- Scan new QR code

### Gmail API Errors

**Re-authenticate:**
```bash
rm gmail_token.json
python gmail_watcher.py
```

**Check credentials:**
- Verify `credentials.json` exists
- Ensure Gmail API is enabled in Google Cloud Console

---

## 📈 Performance

### Resource Usage

- **Memory**: ~200MB (all components running)
- **CPU**: <10% (idle), ~20% (active processing)
- **Network**: ~5KB/s (polling)
- **Disk**: Minimal (logs and task files)

### Optimization Tips

1. **Adjust polling intervals** - Reduce frequency for lower resource usage
2. **Use background mode** - Run watchers as system services
3. **Enable caching** - Dashboard caches data for faster loading
4. **Limit log retention** - Rotate logs to save disk space

---

## 🔐 Security

### Best Practices

✅ **Never commit credentials** - Use .gitignore for sensitive files
✅ **Use environment variables** - Store secrets in .env
✅ **Enable 2FA** - For Gmail, LinkedIn, Odoo accounts
✅ **Review all approvals** - Never auto-approve sensitive actions
✅ **Audit logs regularly** - Check for unauthorized access
✅ **Use HTTPS** - For production deployments
✅ **Limit API permissions** - Only grant necessary scopes

### Files to Keep Private

- `credentials.json` (Gmail API)
- `gmail_token.json` (Gmail OAuth)
- `.env` (Environment variables)
- `linkedin_session` (LinkedIn session)
- `whatsapp_session_js/` (WhatsApp session)
- `Needs Action/`, `Pending Approval/`, `Approved/`, `Done/` (User data)

---

## 🚢 Deployment

### Production Checklist

- [ ] Update all credentials
- [ ] Configure firewall rules
- [ ] Set up SSL certificates
- [ ] Enable authentication on dashboard
- [ ] Configure backup system
- [ ] Set up monitoring alerts
- [ ] Test all workflows end-to-end
- [ ] Document custom configurations

### Cloud Deployment (Oracle Free Tier)

See `PLATINUM_TIER.md` for complete cloud deployment guide.

---

## 📚 Documentation

- **SKILL.md** - Complete system guide and workflows
- **PLATINUM_TIER.md** - Cloud deployment instructions
- **dashboard/README.md** - Dashboard features and customization
- **engine/README.md** - Technical architecture details

---

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📝 License

MIT License - see LICENSE file for details

---

## 🎓 Support

For issues or questions:
1. Check this README
2. Review documentation in `.claude/skills/`
3. Check browser console (F12) for dashboard issues
4. Review logs in `logs/` folder
5. Verify all components are running

---

## 🌟 Acknowledgments

- **Claude AI** - Intelligent task processing
- **Anthropic** - Claude Code CLI
- **Odoo** - Open-source CRM platform
- **WhatsApp Web.js** - WhatsApp automation
- **Gmail API** - Email integration

---

**Ready to automate? Start all components and drop your first task!** 🚀
