# 🤖 AI Employee Vault - Cloud Automation System

**AI-Powered Business Automation Platform | Cloud-Deployed & Production-Ready**

[![Status](https://img.shields.io/badge/status-production-green)](https://github.com)
[![Version](https://img.shields.io/badge/version-4.0-blue)](https://github.com)
[![Cloud](https://img.shields.io/badge/cloud-Digital%20Ocean-orange)](https://github.com)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Current Features](#current-features)
- [Cloud Automation](#cloud-automation)
- [Local Automation](#local-automation)
- [Architecture](#architecture)
- [Cloud Infrastructure](#cloud-infrastructure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Skills & Documentation](#skills--documentation)
- [Troubleshooting](#troubleshooting)
- [Support](#support)

---

## 🎯 Overview

**AI Employee Vault** is a comprehensive AI-powered business automation platform deployed on Digital Ocean cloud. It automates workflows across **Facebook, Twitter, Email, WhatsApp, LinkedIn, and Odoo ERP** with Claude AI content generation, scheduling, and approval workflows.

### **Key Capabilities**

- ✅ **Multi-Channel Automation** - Facebook, Twitter, Email, WhatsApp, LinkedIn
- ✅ **ERP Integration** - Full Odoo ERP integration (CRM, Sales, Invoicing)
- ✅ **AI-Powered** - Claude AI for professional content generation
- ✅ **Post Scheduling** - Schedule Twitter & Facebook posts
- ✅ **Diagram Generation** - Auto-generate Mermaid diagrams (100% FREE)
- ✅ **Image Upload** - Upload images with posts
- ✅ **Approval Workflows** - Human-in-the-loop approval system
- ✅ **Cloud-Native** - Deployed on Digital Ocean (24/7)
- ✅ **Real-Time Monitoring** - Live dashboard with analytics
- ✅ **Audit Trail** - Complete execution logs

---

## ✨ CURRENT FEATURES

### **1. Facebook Automation** 📘

**Cloud-Based (Fully Automated)**

**Capabilities:**
- ✅ Create posts with AI-generated content
- ✅ Schedule posts for later
- ✅ Upload images with posts
- ✅ Delete posts by ID
- ✅ Reply to comments automatically
- ✅ Lead detection from comments
- ✅ Post analytics and insights
- ✅ Odoo CRM integration for leads

**Workflow:**
```
User creates post → Claude enhances content → 
Approval required → Human approves → 
Posts to Facebook automatically (with image)
```

**API Endpoints:**
```
POST /api/facebook/post      - Create post
POST /api/facebook/schedule  - Schedule post
GET  /api/facebook/posts     - Get recent posts
GET  /api/facebook/analytics - Get analytics
```

---

### **2. Twitter Automation** 🐦

**Cloud-Based (Semi-Automated)**

**Capabilities:**
- ✅ Create tweets with Claude AI enhancement
- ✅ Schedule tweets for specific dates/times
- ✅ Thread creation (multi-tweet)
- ✅ Auto-generate diagrams (Mermaid)
- ✅ Upload images (manual posting)
- ✅ Profile information & analytics

**Free Posting Method:**
- Uses `twitter.com/intent/tweet` (100% FREE)
- No Twitter API payment required
- Human reviews before posting

**API Endpoints:**
```
POST /api/twitter/post       - Create tweet
POST /api/twitter/schedule   - Schedule tweet
GET  /api/twitter/tweets     - Get recent tweets
GET  /api/twitter/profile    - Get profile info
```

---

### **3. Email Automation** 📧

**Cloud-Based (Fully Automated)**

**Capabilities:**
- ✅ Gmail API integration
- ✅ Auto-reply to incoming emails
- ✅ Email templates and drafts
- ✅ Attachment support
- ✅ Email threading

**Workflow:**
```
Gmail Watcher detects new email → 
Creates task in Needs Action/ → 
Claude drafts reply → Human approves → 
Sends via Gmail API
```

---

### **4. WhatsApp Automation** 💬

**Local-Based (Requires Local Session)**

**Capabilities:**
- ✅ Send messages (WhatsApp Web)
- ✅ Auto-reply to messages
- ✅ Group messaging
- ✅ Media support (images, documents)
- ✅ Contact management

**Note:** Requires local browser session for authentication due to WhatsApp Web security.

---

### **5. LinkedIn Automation** 🔗

**Local-Based (Requires Local Session)**

**Capabilities:**
- ✅ Create professional posts
- ✅ Auto-generate content with AI
- ✅ Hashtag optimization
- ✅ Post scheduling
- ✅ Engagement tracking

**Note:** Uses browser automation (Playwright).

---

### **6. Odoo ERP Integration** 🏢

**Cloud-Based (Fully Automated)**

**Capabilities:**
- ✅ Lead creation and management
- ✅ Customer management
- ✅ Sales quotations
- ✅ Invoice generation
- ✅ Inventory tracking
- ✅ Financial reporting

**Modules:**
- CRM (Customer Relationship Management)
- Sales (Quotations, Orders)
- Invoicing (Customer Invoices)
- Inventory (Stock Management)

---

### **7. Post Scheduling** 🕐

**Cloud-Based (Fully Automated)**

**Capabilities:**
- ✅ Schedule Twitter posts
- ✅ Schedule Facebook posts
- ✅ Claude AI enhancement at scheduled time
- ✅ Auto-generate diagrams at scheduled time
- ✅ Human approval required
- ✅ Datetime picker in dashboard
- ✅ View/cancel scheduled posts

**How It Works:**
```
User schedules post → Saved to database → 
Scheduler checks every 60 seconds → 
At scheduled time:
  1. Claude enhances content
  2. Generates diagram (if keywords detected)
  3. Creates approval file
  4. Human approves
  5. Posts automatically
```

---

### **8. Diagram Generation** 🎨

**Cloud-Based (100% FREE)**

**Capabilities:**
- ✅ Auto-detect diagram requests
- ✅ Mermaid code generation via Claude
- ✅ Convert Mermaid → PNG
- ✅ Professional styling with colors
- ✅ No API costs (completely free)

**Supported Diagrams:**
- Flowcharts
- Sequence diagrams
- Class diagrams
- Mind maps
- Marketing funnels
- Gantt charts
- Architecture diagrams
- Process workflows

**Keywords That Trigger Diagrams:**
```
diagram, flowchart, workflow, architecture, 
process, pipeline, graph, funnel, explain,
how it works
```

---

### **9. Image Upload** 📷

**Cloud-Based (Fully Automated)**

**Capabilities:**
- ✅ Upload images via dashboard
- ✅ Attach images to Facebook posts
- ✅ Attach images to Twitter posts (manual)
- ✅ Supports PNG, JPG, GIF
- ✅ Automatic file management

**Workflow:**
```
User uploads image in dashboard → 
Saved to Post_Images/ folder → 
Task created with image_path in YAML → 
Orchestrator reads image_path → 
Creates approval file with image → 
Human approves → 
Posts with image attached
```

---

## ☁️ CLOUD AUTOMATION

### **Running on Digital Ocean Cloud (24/7)**

| Service | Status | Description |
|---------|--------|-------------|
| **Facebook Manager** | ✅ Active | Post creation, scheduling, analytics |
| **Twitter Manager** | ✅ Active | Tweet creation, scheduling, threads |
| **Gmail Manager** | ✅ Active | Email sending, auto-replies |
| **Odoo Manager** | ✅ Active | CRM, Sales, Invoicing |
| **Scheduler Service** | ✅ Active | Scheduled posts (checks every 60s) |
| **Orchestrator** | ✅ Active | AI task processing with Claude |
| **Execute Approved** | ✅ Active | Executes approved actions |
| **Dashboard** | ✅ Active | Web UI (Port 5000) |
| **Gmail Watcher** | ✅ Active | Monitors Gmail inbox |
| **Inbox Watcher** | ✅ Active | Monitors file drops |

### **Cloud Features:**
- ✅ **24/7 Operation** - Always running
- ✅ **Auto-Restart** - PM2 process management
- ✅ **Logging** - Complete audit trail
- ✅ **Monitoring** - Real-time status
- ✅ **Scalable** - Easy to upgrade resources

---

## 💻 LOCAL AUTOMATION

### **Running on Local Machine (On-Demand)**

| Service | Status | Description |
|---------|--------|-------------|
| **WhatsApp Watcher** | ⚠️ Local Required | WhatsApp Web automation |
| **LinkedIn Watcher** | ⚠️ Local Required | LinkedIn browser automation |
| **Claude Code CLI** | ⚠️ Local Required | AI content generation |

### **Why Local Required:**

**WhatsApp:**
- WhatsApp Web requires active browser session
- QR code authentication needed
- Cannot run on cloud without violating ToS

**LinkedIn:**
- LinkedIn doesn't have public API for posting
- Uses browser automation (Playwright)
- Requires active login session

**Claude Code:**
- Claude Code CLI runs locally
- Cloud server doesn't have Claude CLI access
- Uses local Claude subscription

---

## 🏗️ ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────┐
│                    DIGITAL OCEAN CLOUD (24/7)                   │
│                     IP: 167.71.237.77                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Facebook   │  │    Twitter   │  │    Gmail     │          │
│  │   Manager    │  │   Manager    │  │   Manager    │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           │                                     │
│                  ┌────────▼────────┐                            │
│                  │  Orchestrator   │                            │
│                  │   (AI Engine)   │                            │
│                  └────────┬────────┘                            │
│                           │                                     │
│         ┌─────────────────┼─────────────────┐                   │
│         │                 │                 │                   │
│  ┌──────▼───────┐  ┌──────▼───────┐  ┌──────▼───────┐          │
│  │   Scheduler  │  │    Odoo      │  │  Dashboard   │          │
│  │   Service    │  │   Manager    │  │   (Web UI)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                 │
│  PM2 Processes (6):                                            │
│  - orchestrator      - execute-approved                        │
│  - dashboard         - post-scheduler                          │
│  - gmail-watcher     - inbox-watcher                           │
│                                                                 │
│  Ports: 5000 (Dashboard), 8069 (Odoo)                          │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ HTTPS
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    LOCAL MACHINE (On-Demand)                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   WhatsApp   │  │   Browser    │  │   Claude     │          │
│  │   Session    │  │   Access     │  │   Code CLI   │          │
│  │  (Required)  │  │              │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ☁️ CLOUD INFRASTRUCTURE

### **Hosting Provider: Digital Ocean**

| Component | Specification | Details |
|-----------|--------------|---------|
| **Droplet** | 4GB RAM / 2 CPU | Ubuntu 24.04 LTS |
| **Location** | New York (NYC1) | US East Coast |
| **Public IP** | 167.71.237.77 | Static IP |
| **Storage** | 80GB SSD | Application + Data |
| **Uptime** | 99.9% SLA | 24/7 Operation |

### **PM2 Process Management**

| Process Name | Purpose | Port |
|--------------|---------|------|
| **dashboard** | Web dashboard (Flask) | 5000 |
| **orchestrator** | AI task processing | - |
| **execute-approved** | Execute approved actions | - |
| **post-scheduler** | Scheduled post processing | - |
| **gmail-watcher** | Gmail inbox monitoring | - |
| **inbox-watcher** | General inbox monitoring | - |

---

## 🌐 ACCESS URLs

### **Production Environment**

| Service | URL | Credentials | Purpose |
|---------|-----|-------------|---------|
| **Dashboard** | http://167.71.237.77:5000 | Admin | Main automation control panel |
| **Odoo ERP** | http://167.71.237.77:8069 | admin / admin | ERP system |
| **PM2 Monitor** | SSH Access | root | Process monitoring |

### **Access Instructions**

#### **1. Dashboard Access**
```
URL: http://167.71.237.77:5000
Username: admin
Password: [Contact Admin]
```

**Features:**
- Create and manage automation tasks
- Schedule Twitter & Facebook posts
- Upload images with posts
- Approve/reject pending actions
- View execution logs and analytics
- Monitor system health

#### **2. SSH Access (Admin Only)**
```bash
ssh -i "your-private-key.pem" root@167.71.237.77
```

**Common Commands:**
```bash
# Check system status
pm2 status

# View logs
pm2 logs orchestrator --lines 50
pm2 logs execute-approved --lines 50
pm2 logs dashboard --lines 50
pm2 logs post-scheduler --lines 50

# Restart services
pm2 restart all

# Monitor resources
htop
df -h
```

---

## 🚀 INSTALLATION

### **Prerequisites**

- Digital Ocean account
- Domain name (optional)
- Facebook Developer account
- Twitter Developer account (FREE tier)
- Google Cloud account (for Gmail API)
- Odoo subscription (or Odoo Community)

### **Step 1: Deploy to Digital Ocean**

```bash
# Create droplet
Digital Ocean Dashboard → Create Droplet
- Image: Ubuntu 24.04 LTS
- Size: 4GB RAM / 2 CPU
- Region: New York (NYC1)
```

### **Step 2: Install Dependencies**

```bash
# SSH into server
ssh -i "your-key.pem" root@167.71.237.77

# Update system
apt update && apt upgrade -y

# Install Python
apt install python3 python3-pip python3-venv -y

# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install nodejs -y

# Install PM2
npm install -g pm2

# Install Docker (for Odoo)
apt install docker.io docker-compose -y
```

### **Step 3: Deploy Application**

```bash
# Clone repository
cd /home
git clone https://github.com/your-org/ai-employee-vault.git
cd ai-employee-vault

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies
npm install

# Start services
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### **Step 4: Deploy Odoo**

```bash
# Start Odoo container
docker run -d -p 8069:8069 --name odoo \
  -e ODOO_DATABASE=ai_employee_db \
  -e ODOO_ADMIN_PASSWORD=admin \
  odoo:17.0
```

### **Step 5: Start Scheduler Service**

```bash
# Add scheduler to PM2
pm2 start scheduler/main_scheduler.py --name post-scheduler

# Save and restart
pm2 save
pm2 restart all
```

---

## ⚙️ CONFIGURATION

### **Environment Variables (.env)**

```bash
# Facebook Configuration
FACEBOOK_PAGE_TOKEN=EAAGmX...
FACEBOOK_PAGE_ID=976642828873094

# Twitter Configuration
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret

# Gmail Configuration
GMAIL_CREDENTIALS_PATH=/home/ai-employee-vault/credentials.json
GMAIL_TOKEN_PATH=/home/ai-employee-vault/gmail_token.json

# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee_db
ODOO_USERNAME=admin
ODOO_PASSWORD=admin

# System Configuration
BASE_DIR=/home/ai-employee-vault
LOGS_DIR=/home/ai-employee-vault/logs
```

---

## 📖 SKILLS & DOCUMENTATION

### **Claude Skills** (In `.claude/skills/` folder)

| Skill | Purpose | Use For |
|-------|---------|---------|
| **enterprise_saas_extension.md** | Enterprise transformation guide | Future SaaS development |
| **complete_system_documentation.md** | Full system documentation | Onboarding, troubleshooting |
| **facebook_automation.md** | Facebook API guide | Facebook automation |
| **twitter_automation.md** | Twitter API guide | Twitter automation |

### **How to Use Skills**

```
@enterprise_saas_extension Show me Phase 1 implementation
@complete_system_documentation How does Gmail watcher work?
@facebook_automation How to create posts with images?
@twitter_automation How to schedule tweets?
```

### **Additional Documentation**

| Document | Purpose |
|----------|---------|
| `SCHEDULING_IMPLEMENTATION.md` | Scheduling feature guide |
| `MERMAID_DIAGRAM_IMPLEMENTATION.md` | Diagram generation guide |
| `IMAGE_UPLOAD_COMPLETE.md` | Image upload guide |
| `DEPLOYMENT_QUICK_START.md` | Quick deployment guide |

---

## 🔧 TROUBLESHOOTING

### **Common Issues**

#### **1. Orchestrator Not Processing Tasks**

**Symptoms:**
- Tasks in Needs Action/ not being processed
- No logs from orchestrator

**Solution:**
```bash
# Check if orchestrator is running
pm2 status orchestrator

# If stopped, start it
pm2 start orchestrator

# Check logs for errors
pm2 logs orchestrator --lines 100
```

#### **2. Images Not Posting to Facebook**

**Symptoms:**
- Logs show "Posting text only"
- Image exists in Post_Images/

**Solution:**
```bash
# Check if image_path in approval file
cat Approved/APPROVAL_facebook_post_*.md | grep image_path

# Restart execute-approved
pm2 restart execute-approved
```

#### **3. Scheduler Not Running**

**Symptoms:**
- Scheduled posts not being processed
- No logs from post-scheduler

**Solution:**
```bash
# Check if scheduler is running
pm2 status post-scheduler

# Check server time (timezone issue)
date
timedatectl

# Fix timezone if needed
timedatectl set-timezone Asia/Karachi

# Restart scheduler
pm2 restart post-scheduler
```

#### **4. Emoji Encoding Broken**

**Symptoms:**
- Emojis showing as `ðŸš€` instead of `🚀`

**Solution:**
```python
# In orchestrator.py, ensure UTF-8 encoding
result = subprocess.run(
    [claude_path, '-p'],
    input=claude_prompt,
    capture_output=True,
    text=True,
    timeout=120,
    shell=True,
    encoding='utf-8',
    errors='replace'
)
```

---

## 🛠️ SUPPORT

### **Getting Help**

1. **Check Documentation:**
   - Read skills in `.claude/skills/` folder
   - Review troubleshooting section
   - Check implementation guides

2. **View Logs:**
   ```bash
   pm2 logs --lines 100
   ```

3. **Contact Support:**
   - Email: support@aiemployeevault.com
   - Slack: #ai-employee-vault
   - GitHub Issues: Create issue with logs

---

## 📊 CURRENT STATUS

| Feature | Cloud | Local | Status |
|---------|-------|-------|--------|
| **Facebook Posts** | ✅ | - | Fully Automated |
| **Facebook Scheduling** | ✅ | - | Fully Automated |
| **Twitter Posts** | ✅ | - | Semi-Automated |
| **Twitter Scheduling** | ✅ | - | Fully Automated |
| **Email (Gmail)** | ✅ | - | Fully Automated |
| **WhatsApp** | - | ✅ | Local Session Required |
| **LinkedIn** | - | ✅ | Local Session Required |
| **Odoo CRM** | ✅ | - | Fully Automated |
| **Diagram Generation** | ✅ | - | Fully Automated |
| **Image Upload** | ✅ | - | Fully Automated |
| **Scheduling** | ✅ | - | Fully Automated |

---

**Version:** 4.0 (Production Ready)  
**Last Updated:** March 2026  
**Status:** Cloud-Deployed ✅ | Production-Ready ✅
