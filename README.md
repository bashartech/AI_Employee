# 🤖 AI Employee Vault - Cloud Automation System

**Enterprise-Grade AI-Powered Business Automation Platform**

[![Status](https://img.shields.io/badge/status-production-green)](https://github.com)
[![Version](https://img.shields.io/badge/version-3.0-blue)](https://github.com)
[![License](https://img.shields.io/badge/license-proprietary-red)](https://github.com)

---

## 📋 Table of Contents

- [Overview](#overview)
- [What's New in v3.0](#whats-new-in-v30)
- [Architecture](#architecture)
- [Cloud Infrastructure](#cloud-infrastructure)
- [Access URLs](#access-urls)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)
- [Support](#support)

---

## 🎯 Overview

AI Employee Vault is a comprehensive cloud-based automation platform that leverages AI to automate business processes across multiple channels including **Facebook, Twitter, Email, WhatsApp, LinkedIn, and Odoo ERP**. Built for enterprises seeking to streamline operations through intelligent automation.

### **Key Capabilities**

- ✅ **Multi-Channel Automation** - Facebook, Twitter, Email, WhatsApp, LinkedIn
- ✅ **ERP Integration** - Full Odoo ERP integration (CRM, Sales, Invoicing)
- ✅ **AI-Powered** - Claude AI for professional content generation
- ✅ **Scheduling** - Schedule posts for Twitter & Facebook
- ✅ **Approval Workflows** - Human-in-the-loop approval system
- ✅ **Cloud-Native** - Deployed on Digital Ocean cloud infrastructure
- ✅ **Real-Time Monitoring** - Live dashboard with analytics
- ✅ **Audit Trail** - Complete execution logs and compliance tracking

---

## 🎉 What's New in v3.0

### **✨ Post Scheduling**
- **Twitter Scheduling** - Schedule tweets for specific dates/times
- **Facebook Scheduling** - Schedule posts with automatic approval workflow
- **Claude Enhancement** - All scheduled posts enhanced by Claude AI before posting
- **Approval Required** - Human approval still required even for scheduled posts

### **🐦 Twitter Integration**
- **Create Tweets** - Professional tweets with Claude AI enhancement
- **Thread Support** - Create multi-tweet threads
- **Scheduling** - Schedule tweets for optimal engagement times
- **Profile Management** - View profile info and analytics
- **Free Posting** - Uses twitter.com/intent/tweet (100% FREE, no API payment needed)

### **📘 Facebook Complete Automation**
- **Post Creation** - AI-generated professional posts
- **Comment Management** - Auto-reply to comments, detect leads
- **Lead Generation** - Extract leads from comments, create Odoo entries
- **Analytics** - Page insights, post performance tracking
- **Scheduling** - Schedule posts for later publishing

### **🤖 Claude AI Integration**
- **Professional Content** - All posts enhanced by Claude before approval
- **Consistent Quality** - Same enhancement for scheduled and immediate posts
- **Smart Fallback** - Uses original content if Claude unavailable

### **📊 Enhanced Dashboard**
- **Twitter Management UI** - Create, schedule, and view tweets
- **Facebook Management UI** - Complete Facebook page management
- **Schedule Tabs** - Dedicated scheduling interface for both platforms
- **Datetime Picker** - Easy scheduling with visual datetime selector

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DIGITAL OCEAN CLOUD (24/7)                   │
│                     IP: 167.71.237.77                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Facebook   │  │    Twitter   │  │    Email     │          │
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
│  │   LinkedIn   │  │    Odoo      │  │  Dashboard   │          │
│  │   Manager    │  │   Manager    │  │   (Web UI)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                 │
│  ┌─────────────────────────────────────────────────┐           │
│  │           Scheduler Service (NEW v3.0)          │           │
│  │  - Checks every 60 seconds for scheduled posts  │           │
│  │  - Creates approval files at scheduled time     │           │
│  │  - Uses Claude for content enhancement          │           │
│  └─────────────────────────────────────────────────┘           │
│                                                                 │
│  Ports: 5000 (Dashboard), 8069 (Odoo)                          │
└─────────────────────────────────────────────────────────────────┘
                           │
                           │ HTTPS
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    LOCAL MACHINE (On-Demand)                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   WhatsApp   │  │   Browser    │  │   Mobile     │          │
│  │   Session    │  │   Access     │  │   Apps       │          │
│  │  (Required)  │  │              │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## ☁️ Cloud Infrastructure

### **Hosting Provider: Digital Ocean**

| Component | Specification | Details |
|-----------|--------------|---------|
| **Droplet** | 4GB RAM / 2 CPU | Ubuntu 24.04 LTS |
| **Location** | New York (NYC1) | US East Coast |
| **Public IP** | 167.71.237.77 | Static IP |
| **Storage** | 80GB SSD | Application + Data |
| **Uptime** | 99.9% SLA | 24/7 Operation |

### **Cloud Services**

| Service | Purpose | Status |
|---------|---------|--------|
| **Facebook Graph API** | Post creation, deletion, analytics | ✅ Active |
| **Twitter API** | Tweet posting (FREE tier: 1,500/month) | ✅ Active |
| **Gmail API** | Email sending, receiving, management | ✅ Active |
| **Odoo ERP** | CRM, Sales, Invoicing, Inventory | ✅ Active |
| **WhatsApp Business** | Message automation (Local Session) | ⚠️ Local Required |
| **LinkedIn API** | Post automation (Local Session) | ⚠️ Local Required |

### **PM2 Process Management**

| Process Name | Purpose | Port |
|--------------|---------|------|
| **dashboard** | Web dashboard (Flask) | 5000 |
| **orchestrator** | AI task processing | - |
| **execute-approved** | Execute approved actions | - |
| **post-scheduler** | Scheduled post processing (NEW) | - |
| **gmail-watcher** | Gmail inbox monitoring | - |
| **inbox-watcher** | General inbox monitoring | - |

---

## 🌐 Access URLs

### **Production Environment**

| Service | URL | Credentials | Purpose |
|---------|-----|-------------|---------|
| **Dashboard** | http://167.71.237.77:5000 | Admin | Main automation control panel |
| **Odoo ERP** | http://167.71.237.77:8069 | admin / admin | ERP system (CRM, Sales, etc.) |
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
- Approve/reject pending actions
- View execution logs and analytics
- Monitor system health

#### **2. Odoo ERP Access**

```
URL: http://167.71.237.77:8069
Username: admin
Password: admin
Database: ai_employee_db
```

**Modules Available:**
- CRM (Customer Relationship Management)
- Sales (Quotations, Orders)
- Invoicing (Customer Invoices)
- Inventory (Stock Management)
- Accounting (Financial Reports)

#### **3. SSH Access (Admin Only)**

```bash
ssh -i "your-private-key.pem" root@167.71.237.77
```

**Commands:**
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

## ✨ Features

### **1. Facebook Automation** 📘

**Capabilities:**
- ✅ Create posts with AI-generated content
- ✅ Schedule posts for later
- ✅ Delete posts by ID
- ✅ Reply to comments automatically
- ✅ Hide inappropriate comments
- ✅ Lead detection from comments
- ✅ Post analytics and insights
- ✅ Odoo CRM integration for leads

**Approval Workflow:**
```
User Creates Post → AI Generates Content → Pending Approval →
Human Approval → Execute → Posted to Facebook → Done
```

**Scheduling Workflow:**
```
User Schedules Post → Save to Database → Scheduler Checks Every 60s →
At Scheduled Time: Claude Enhances Content → Create Approval →
Human Approval → Execute → Posted to Facebook → Done
```

**API Endpoints:**
```
POST /api/facebook/post      - Create post
POST /api/facebook/schedule  - Schedule post (NEW)
GET  /api/facebook/posts     - Get recent posts
GET  /api/facebook/analytics - Get analytics
GET  /api/facebook/comments  - Get comments
```

---

### **2. Twitter Automation** 🐦 (NEW v3.0)

**Capabilities:**
- ✅ Create tweets with Claude AI enhancement
- ✅ Schedule tweets for specific dates/times
- ✅ Thread creation (multi-tweet posts)
- ✅ Professional content generation
- ✅ Hashtag optimization
- ✅ Profile information viewing
- ✅ Recent tweets display
- ✅ FREE posting via twitter.com/intent/tweet

**Approval Workflow:**
```
User Creates Tweet → Claude Enhances Content → Pending Approval →
Human Approval → Opens Twitter → User Clicks Tweet → Posted
```

**Scheduling Workflow:**
```
User Schedules Tweet → Save to Database → Scheduler Checks Every 60s →
At Scheduled Time: Claude Enhances → Create Approval →
Human Approval → Opens Twitter → User Clicks Tweet → Posted
```

**API Endpoints:**
```
POST /api/twitter/post       - Create tweet
POST /api/twitter/schedule   - Schedule tweet (NEW)
GET  /api/twitter/tweets     - Get recent tweets
GET  /api/twitter/profile    - Get profile info
```

**Twitter API Limits (FREE Tier):**
- 1,500 tweets per month
- No reading capabilities (payment required)
- Solution: Use twitter.com/intent/tweet for 100% FREE posting

---

### **3. Email Automation** 📧

**Capabilities:**
- ✅ Send emails via Gmail API
- ✅ Auto-reply to incoming emails
- ✅ Email templates and drafts
- ✅ Attachment support
- ✅ Email threading
- ✅ Delivery tracking

**Approval Workflow:**
```
Incoming Email → AI Drafts Response → Pending Approval →
Human Review → Send via Gmail → Logged
```

**Integration:**
- Gmail API (OAuth 2.0)
- SMTP fallback
- Custom domain support

---

### **4. WhatsApp Automation** 💬

**Capabilities:**
- ✅ Send messages to contacts
- ✅ Auto-reply to messages
- ✅ Group messaging
- ✅ Media support (images, documents)
- ✅ Message scheduling

**Architecture:**
```
Cloud: Message queuing, AI content generation
Local: WhatsApp Web session (required for sending)
```

**Note:** WhatsApp requires local browser session for authentication due to WhatsApp Web security.

---

### **5. LinkedIn Automation** 🔗

**Capabilities:**
- ✅ Create professional posts
- ✅ Auto-generate content with AI
- ✅ Hashtag optimization
- ✅ Post scheduling
- ✅ Engagement tracking

**Architecture:**
```
Cloud: Content generation, approval workflow
Local: LinkedIn session (for posting)
```

---

### **6. Odoo ERP Integration** 🏢

**Capabilities:**
- ✅ Lead creation and management
- ✅ Customer management
- ✅ Sales quotations
- ✅ Invoice generation
- ✅ Inventory tracking
- ✅ Financial reporting

**Modules:**
```
CRM Module:
- Lead tracking
- Opportunity management
- Pipeline visualization
- Facebook lead integration

Sales Module:
- Quotation creation
- Order processing
- Customer portal

Invoicing Module:
- Invoice generation
- Payment tracking
- Financial reports

Inventory Module:
- Stock management
- Product tracking
- Warehouse operations
```

---

### **7. Post Scheduling** 🕐 (NEW v3.0)

**Capabilities:**
- ✅ Schedule Twitter posts
- ✅ Schedule Facebook posts
- ✅ Claude AI enhancement at scheduled time
- ✅ Human approval still required
- ✅ Datetime picker in dashboard
- ✅ View all scheduled posts
- ✅ Cancel scheduled posts

**How It Works:**
```
1. User creates post in dashboard
2. Selects "Schedule" tab
3. Enters content and picks datetime
4. Saved to SQLite database
5. Scheduler checks every 60 seconds
6. At scheduled time:
   - Claude generates professional content
   - Creates approval file in Pending Approval/
7. Human reviews and approves
8. execute_approved.py posts automatically
```

**Database Schema:**
```sql
CREATE TABLE scheduled_posts (
    id INTEGER PRIMARY KEY,
    platform TEXT,           -- 'twitter' or 'facebook'
    content TEXT,
    scheduled_time DATETIME,
    status TEXT,             -- pending, processed, failed
    created_at DATETIME,
    approval_file TEXT,
    hashtags TEXT,
    is_thread INTEGER
);
```

---

## 🚀 Installation

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

## ⚙️ Configuration

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

## 📊 Dashboard Features

### **Twitter Management Section**
- ✍️ **Create Post** - Create tweets with Claude enhancement
- 🕐 **Schedule Post** - Schedule tweets for later
- 📝 **Recent Tweets** - View recent tweets and engagement
- ℹ️ **Profile** - View Twitter profile information

### **Facebook Management Section**
- ✍️ **Create Post** - Create posts with Claude enhancement
- 🕐 **Schedule Post** - Schedule posts for later
- 📝 **Manage Posts** - View and manage Facebook posts
- 📊 **Analytics** - View page insights and metrics
- ℹ️ **Page Info** - View Facebook page details

### **Scheduling UI**
- Datetime picker for easy scheduling
- Timezone-aware scheduling
- View all scheduled posts
- Cancel scheduled posts
- Success/error notifications

---

## 🔧 Troubleshooting

### **Scheduler Not Running**

```bash
# Check PM2 status
pm2 status post-scheduler

# View logs
pm2 logs post-scheduler

# Restart scheduler
pm2 restart post-scheduler
```

### **Claude Not Enhancing Scheduled Posts**

```bash
# Check Claude CLI path
which claude

# Test Claude
claude -p "Hello"

# Update path in scheduler if needed
# scheduler/twitter_scheduler.py
# scheduler/facebook_scheduler.py
```

### **Scheduled Posts Not Posting**

```bash
# Check scheduler logs
pm2 logs post-scheduler --lines 100

# Check database
cd /home/ai-employee-vault
python3 -c "from scheduler.scheduler_db import get_pending_posts; print(get_pending_posts())"

# Verify time synchronization
timedatectl
```

---

## 📚 Additional Documentation

- [SCHEDULING_IMPLEMENTATION.md](./SCHEDULING_IMPLEMENTATION.md) - Complete scheduling guide
- [SCHEDULING_CLAUDE_FIX.md](./SCHEDULING_CLAUDE_FIX.md) - Claude integration for scheduling
- [TWITTER_OAUTH1_SETUP.md](./TWITTER_OAUTH1_SETUP.md) - Twitter OAuth setup
- [DEPLOYMENT_QUICK_START.md](./DEPLOYMENT_QUICK_START.md) - Quick deployment guide

---

## 🛠️ Support

For issues, questions, or feature requests, please contact the development team.

**Development Team:**
- Lead Developer: [Your Name]
- Email: [your.email@example.com]
- Slack: #ai-employee-vault

---

**Version:** 3.0.0  
**Last Updated:** March 2026  
**Status:** Production Ready ✅
