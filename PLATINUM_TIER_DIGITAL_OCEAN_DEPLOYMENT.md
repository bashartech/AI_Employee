# 🌐 Platinum Tier: Digital Ocean Cloud Deployment Guide
## Complete Step-by-Step Instructions for Deploying AI Employee Vault on Digital Ocean

**Last Updated:** March 11, 2026  
**Tier:** Platinum (Production-Ready Cloud Deployment)  
**Estimated Time:** 3-4 hours  
**Cost:** ~$12-24/month (Digital Ocean Droplet + backups)

---

## 📋 Table of Contents

1. [Overview & Architecture](#overview--architecture)
2. [Prerequisites](#prerequisites)
3. [Phase 1: Digital Ocean VM Setup](#phase-1-digital-ocean-vm-setup)
4. [Phase 2: Server Configuration](#phase-2-server-configuration)
5. [Phase 3: Application Deployment](#phase-3-application-deployment)
6. [Phase 4: Odoo Community Deployment](#phase-4-odoo-community-deployment)
7. [Phase 5: Security & HTTPS](#phase-5-security--https)
8. [Phase 6: Monitoring & Health Checks](#phase-6-monitoring--health-checks)
9. [Phase 7: Work-Zone Specialization](#phase-7-work-zone-specialization)
10. [Phase 8: Vault Sync Setup](#phase-8-vault-sync-setup)
11. [Troubleshooting](#troubleshooting)
12. [Cost Breakdown](#cost-breakdown)

---

## 🏗️ Overview & Architecture

### Platinum Tier Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DIGITAL OCEAN CLOUD VM                       │
│                    (24/7 Always-On Agent)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Gmail        │  │ LinkedIn     │  │ Odoo         │          │
│  │ Watcher      │  │ Watcher      │  │ Community    │          │
│  │ (Draft Only) │  │ (Draft Only) │  │ (Local)      │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └─────────────────┴─────────────────┘                   │
│                           │                                     │
│                  ┌────────▼────────┐                            │
│                  │ Cloud Agent     │                            │
│                  │ (Drafts &       │                            │
│                  │  Social Posts)  │                            │
│                  └────────┬────────┘                            │
│                           │                                     │
│                  /Updates/ or /Signals/                         │
│                           │                                     │
└───────────────────────────┼─────────────────────────────────────┘
                            │ Git Sync (Vault)
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    LOCAL MACHINE (Your Laptop)                  │
│                    (Approval & Execution)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ WhatsApp     │  │ Banking/     │  │ Dashboard    │          │
│  │ Session      │  │ Payments     │  │ & Approval   │          │
│  │ (Local Only) │  │ (Local Only) │  │ UI           │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                  │
│  /Pending_Approval/ → Human Reviews → /Approved/                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### What Runs Where?

| Component | Location | Purpose |
|-----------|----------|---------|
| **Gmail Watcher** | Cloud | Monitor & draft email responses |
| **LinkedIn Watcher** | Cloud | Create & schedule post drafts |
| **Odoo Community** | Cloud | 24/7 CRM, invoicing, accounting |
| **Cloud Agent** | Cloud | Draft replies, social posts, lead creation |
| **WhatsApp Session** | Local | Send WhatsApp messages (requires phone) |
| **Banking/Payments** | Local | Secure payment operations |
| **Dashboard** | Local | Human approval UI |
| **Final Approval** | Local | Human reviews before send/post |

---

## ✅ Prerequisites

### Required Accounts & Tools

1. **Digital Ocean Account** - [Sign up here](https://www.digitalocean.com/)
   - Free $200 credit for 60 days (new users)
   - Credit card required for verification

2. **Domain Name** (optional but recommended)
   - For HTTPS and professional access
   - Can use Digital Ocean's free subdomain or buy elsewhere

3. **GitHub Account**
   - For version control and vault sync

4. **SSH Key Pair**
   - Generate if you don't have one: `ssh-keygen -t ed25519`

5. **Local Software**
   ```bash
   # Install on your local machine
   - Git
   - SSH client
   - Code editor (VS Code, etc.)
   ```

### Estimated Costs

| Resource | Monthly Cost | Notes |
|----------|--------------|-------|
| Basic Droplet (2GB RAM) | $12 | Minimum for this project |
| Premium Droplet (4GB RAM) | $24 | Recommended for Odoo + all watchers |
| Backups | $2.40 | 20% of droplet cost |
| Domain (optional) | $10-15/year | Optional |
| **Total** | **$14.40 - $26.40/month** | With backups |

---

## 🚀 Phase 1: Digital Ocean VM Setup

### Step 1.1: Create a New Droplet

1. **Login to Digital Ocean**
   - Go to [cloud.digitalocean.com](https://cloud.digitalocean.com/)
   - Login or create account

2. **Create Droplet**
   - Click "Create" → "Droplets"
   - Choose region (closest to you for lower latency):
     - **US/East:** New York (NYC1)
     - **US/West:** San Francisco (SFO1)
     - **Europe:** London (LON1), Frankfurt (FRA1)
     - **Asia:** Singapore (SGP1), Bangalore (BLR1)

3. **Choose Image**
   - Select: **Ubuntu 24.04 LTS x64**
   - This is the most stable and well-supported option

4. **Choose Plan**
   - **Minimum:** Basic → Regular → 2GB RAM / 1 CPU ($12/month)
   - **Recommended:** Basic → Regular → 4GB RAM / 2 CPU ($24/month)
   - For Odoo + all watchers, 4GB is better

5. **Add SSH Key**
   - Click "New SSH Key"
   - Copy your public key: `cat ~/.ssh/id_ed25519.pub` (Mac/Linux)
     or `type %USERPROFILE%\.ssh\id_ed25519.pub` (Windows)
   - Paste and give it a name (e.g., "AI Employee Vault")

6. **Configure Settings**
   - **Hostname:** `ai-employee-vault` (or your preferred name)
   - **Enable backups:** ✅ Recommended ($2.40/month)
   - **Enable monitoring:** ✅ Free and useful
   - **Add tags:** `ai-automation`, `production`

7. **Create Droplet**
   - Click "Create Droplet"
   - Wait 2-5 minutes for provisioning

### Step 1.2: Verify SSH Access

```bash
# Test SSH connection (replace with your droplet IP)
ssh root@your_droplet_ip

# Example:
ssh root@159.65.123.45

# You should see:
# Welcome to Ubuntu 24.04 LTS (GNU/Linux ...)
# root@ai-employee-vault:~#
```

### Step 1.3: Initial Server Setup

```bash
# Update system packages
apt update && apt upgrade -y

# Install essential tools
apt install -y \
    git \
    curl \
    wget \
    vim \
    htop \
    ufw \
    fail2ban \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    nodejs \
    npm \
    postgresql \
    postgresql-contrib \
    nginx \
    certbot \
    python3-certbot-nginx \
    docker.io \
    docker-compose

# Verify installations
python3 --version  # Should show Python 3.10+
node --version     # Should show Node 18+
docker --version   # Should show Docker 20+
```

### Step 1.4: Create Non-Root User (Security Best Practice)

```bash
# Create new user
adduser aivault

# Add to sudo group
usermod -aG sudo aivault

# Switch to new user
su - aivault

# Copy SSH keys
mkdir -p /home/aivault/.ssh
cp /root/.ssh/authorized_keys /home/aivault/.ssh/
chown -R aivault:aivault /home/aivault/.ssh
chmod 700 /home/aivault/.ssh
chmod 600 /home/aivault/.ssh/authorized_keys

# Test login (open new terminal)
ssh aivault@your_droplet_ip
```

---

## ⚙️ Phase 2: Server Configuration

### Step 2.1: Configure Firewall

```bash
# Enable UFW firewall
sudo ufw allow OpenSSH
sudo ufw allow http
sudo ufw allow https
sudo ufw allow 8069  # Odoo default port
sudo ufw allow 5000  # Dashboard port (if hosting on cloud)

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status verbose
```

### Step 2.2: Install Python Dependencies

```bash
# Create Python virtual environment
cd /home/aivault
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install system dependencies
sudo apt install -y \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    libssl-dev
```

### Step 2.3: Install Node.js Dependencies

```bash
# Install latest Node.js (if apt version is old)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install global packages
sudo npm install -g pm2
# PM2 will keep our Node.js processes running 24/7
```

### Step 2.4: Setup Project Directory

```bash
# Create project structure
mkdir -p /home/aivault/ai-employee-vault
cd /home/aivault/ai-employee-vault

# Create necessary folders
mkdir -p \
    Inbox/Processed \
    Needs_Action \
    Pending_Approval \
    Approved \
    Done \
    Rejected \
    Send_Queue \
    Odoo_Data/{Leads,Quotations,Invoices,CEO_Briefings} \
    Logs \
    .claude/skills \
    engine \
    mcp_servers \
    dashboard
```

---

## 📦 Phase 3: Application Deployment

### Step 3.1: Clone or Upload Project

**Option A: Clone from GitHub (Recommended)**

```bash
# On your LOCAL machine, commit and push your project
cd D:\DATA\HACKATHON_0\AI_Employee_Vault
git init
git add .
git commit -m "Initial commit - AI Employee Vault"
git branch -M main
git remote add origin https://github.com/yourusername/ai-employee-vault.git
git push -u origin main

# On DIGITAL OCEAN server
cd /home/aivault
git clone https://github.com/yourusername/ai-employee-vault.git
cd ai-employee-vault
```

**Option B: Upload via SCP (Alternative)**

```bash
# On LOCAL machine (PowerShell or terminal)
scp -r D:\DATA\HACKATHON_0\AI_Employee_Vault\* aivault@your_droplet_ip:/home/aivault/ai-employee-vault/
```

### Step 3.2: Install Python Dependencies

```bash
cd /home/aivault/ai-employee-vault

# Activate virtual environment
source /home/aivault/venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Install Playwright browsers (for WhatsApp/LinkedIn automation)
playwright install chromium
playwright install-deps chromium
```

### Step 3.3: Install Node.js Dependencies

```bash
cd /home/aivault/ai-employee-vault

# Install Node packages
npm install

# Install PM2 for process management
sudo npm install -g pm2
```

### Step 3.4: Configure Environment Variables

```bash
cd /home/aivault/ai-employee-vault

# Copy example env file
cp .env.example .env

# Edit .env file
nano .env
```

**Update `.env` with your credentials:**

```bash
# AI Configuration (using Qwen or Claude)
QWEN_BASE_URL=http://localhost:11434/v1
QWEN_API_KEY=dummy-key
QWEN_MODEL=qwen2.5:latest

# Or use Claude API
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Gmail API Configuration
GMAIL_CREDENTIALS_PATH=/home/aivault/ai-employee-vault/credentials.json
GMAIL_TOKEN_PATH=/home/aivault/ai-employee-vault/gmail_token.json

# Odoo Configuration (local deployment)
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee_db
ODOO_USERNAME=your_odoo_email@example.com
ODOO_PASSWORD=your_odoo_password

# Engine Configuration
LOG_LEVEL=INFO
POLL_INTERVAL=60
MAX_REASONING_ITERATIONS=5

# Approval Settings
REQUIRE_APPROVAL_FOR_FINANCIAL=true
REQUIRE_APPROVAL_FOR_SENSITIVE=true

# Cloud-specific settings
CLOUD_MODE=true
LOCAL_MODE=false
```

### Step 3.5: Setup Gmail API

```bash
# On LOCAL machine first:
# 1. Go to Google Cloud Console: https://console.cloud.google.com
# 2. Create new project
# 3. Enable Gmail API
# 4. Create OAuth 2.0 credentials
# 5. Download credentials.json

# Upload credentials to server
scp credentials.json aivault@your_droplet_ip:/home/aivault/ai-employee-vault/

# On SERVER:
cd /home/aivault/ai-employee-vault

# Run Gmail watcher to authenticate
source /home/aivault/venv/bin/activate
python gmail_watcher.py
# This will open a browser URL - copy it to your LOCAL browser
# Complete OAuth flow and token will be saved
```

### Step 3.6: Setup PM2 Process Management

Create PM2 ecosystem file:

```bash
cd /home/aivault/ai-employee-vault
nano ecosystem.config.js
```

**Add this configuration:**

```javascript
module.exports = {
  apps: [
    {
      name: 'orchestrator',
      script: 'python3',
      args: 'engine/orchestrator.py',
      cwd: '/home/aivault/ai-employee-vault',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
        PATH: '/home/aivault/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
      },
      error_file: '/home/aivault/ai-employee-vault/Logs/orchestrator.err',
      out_file: '/home/aivault/ai-employee-vault/Logs/orchestrator.out',
      log_file: '/home/aivault/ai-employee-vault/Logs/orchestrator.log',
      time: true,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s'
    },
    {
      name: 'execute-approved',
      script: 'python3',
      args: 'execute_approved.py',
      cwd: '/home/aivault/ai-employee-vault',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
        PATH: '/home/aivault/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
      },
      error_file: '/home/aivault/ai-employee-vault/Logs/execute_approved.err',
      out_file: '/home/aivault/ai-employee-vault/Logs/execute_approved.out',
      log_file: '/home/aivault/ai-employee-vault/Logs/execute_approved.log',
      time: true,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s'
    },
    {
      name: 'gmail-watcher',
      script: 'python3',
      args: 'gmail_watcher.py',
      cwd: '/home/aivault/ai-employee-vault',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
        PATH: '/home/aivault/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
      },
      error_file: '/home/aivault/ai-employee-vault/Logs/gmail_watcher.err',
      out_file: '/home/aivault/ai-employee-vault/Logs/gmail_watcher.out',
      log_file: '/home/aivault/ai-employee-vault/Logs/gmail_watcher.log',
      time: true,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s'
    },
    {
      name: 'dashboard',
      script: 'python3',
      args: 'dashboard/app.py',
      cwd: '/home/aivault/ai-employee-vault',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
        PORT: '5000',
        PATH: '/home/aivault/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
      },
      error_file: '/home/aivault/ai-employee-vault/Logs/dashboard.err',
      out_file: '/home/aivault/ai-employee-vault/Logs/dashboard.out',
      log_file: '/home/aivault/ai-employee-vault/Logs/dashboard.log',
      time: true,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s'
    }
  ]
};
```

**Start all processes:**

```bash
cd /home/aivault/ai-employee-vault

# Start all PM2 processes
pm2 start ecosystem.config.js

# Save PM2 configuration (auto-restart on server reboot)
pm2 save

# Setup PM2 to start on boot
pm2 startup
# Copy and run the command it outputs
```

**Useful PM2 Commands:**

```bash
# Check status
pm2 status

# View logs
pm2 logs orchestrator
pm2 logs execute-approved
pm2 logs gmail-watcher
pm2 logs dashboard

# Restart specific process
pm2 restart orchestrator

# Stop all
pm2 stop all

# Start all
pm2 start all

# Monitor in real-time
pm2 monit
```

---

## 🏢 Phase 4: Odoo Community Deployment

### Step 4.1: Deploy Odoo with Docker

```bash
cd /home/aivault

# Create docker-compose file for Odoo
nano docker-compose-odoo.yml
```

**Add this configuration:**

```yaml
version: '3.1'

services:
  web:
    image: odoo:17.0
    depends_on:
      - db
    ports:
      - "8069:8069"
    environment:
      - HOST=db
      - USER=odoo
      - PASSWORD=odoo
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ./odoo/config:/etc/odoo
      - ./odoo/addons:/mnt/extra-addons
    restart: unless-stopped
    networks:
      - odoo-network

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_PASSWORD=odoo
      - POSTGRES_USER=odoo
    volumes:
      - odoo-db-data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - odoo-network

volumes:
  odoo-web-data:
  odoo-db-data:

networks:
  odoo-network:
    driver: bridge
```

**Start Odoo:**

```bash
# Create necessary directories
mkdir -p /home/aivault/odoo/config
mkdir -p /home/aivault/odoo/addons

# Start Odoo containers
cd /home/aivault
docker-compose -f docker-compose-odoo.yml up -d

# Check status
docker-compose -f docker-compose-odoo.yml ps

# View logs
docker-compose -f docker-compose-odoo.yml logs -f web
```

### Step 4.2: Configure Odoo

1. **Access Odoo** (in your browser):
   ```
   http://your_droplet_ip:8069
   ```

2. **Create Database:**
   - Master Password: Choose a strong password (save it!)
   - Database Name: `ai_employee_db`
   - Email: Your admin email
   - Password: Your admin password

3. **Install Apps:**
   - Go to Apps menu
   - Install: **CRM**, **Sales**, **Invoicing**, **Contacts**

4. **Configure Users:**
   - Settings → Users & Companies → Users
   - Create user for AI Employee:
     - Name: AI Employee
     - Email: ai@yourcompany.com
     - Access Rights:
       - CRM: User
       - Sales: User
       - Invoicing: Accountant

### Step 4.3: Update Odoo Configuration

Update `mcp_servers/odoo_server.py`:

```python
self.url = "http://localhost:8069"
self.db = "ai_employee_db"
self.username = "ai@yourcompany.com"
self.password = "your_admin_password"
```

Test connection:

```bash
cd /home/aivault/ai-employee-vault
source /home/aivault/venv/bin/activate
python test_odoo.py
```

---

## 🔒 Phase 5: Security & HTTPS

### Step 5.1: Setup Domain (Optional but Recommended)

1. **Buy or use existing domain**
   - Digital Ocean has domain registration ($5/month)
   - Or use Namecheap, GoDaddy, etc.

2. **Point domain to droplet:**
   - Create A record: `ai.yourdomain.com` → your_droplet_ip

### Step 5.2: Install SSL Certificate (Let's Encrypt)

```bash
# Install certbot (if not already installed)
sudo apt install -y certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d ai.yourdomain.com

# Auto-renewal is configured automatically
# Test renewal:
sudo certbot renew --dry-run
```

### Step 5.3: Configure Nginx Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/ai-employee
```

**Add this configuration:**

```nginx
server {
    listen 80;
    server_name ai.yourdomain.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ai.yourdomain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/ai.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ai.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Dashboard
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Odoo
    location /odoo/ {
        proxy_pass http://127.0.0.1:8069/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable site:**

```bash
sudo ln -s /etc/nginx/sites-available/ai-employee /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 5.4: Setup Fail2Ban (Intrusion Prevention)

```bash
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Configure SSH protection
sudo nano /etc/fail2ban/jail.local
```

**Add:**

```ini
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
```

---

## 📊 Phase 6: Monitoring & Health Checks

### Step 6.1: Setup Health Check Script

```bash
cd /home/aivault/ai-employee-vault
nano health_check.sh
```

**Add:**

```bash
#!/bin/bash

LOG_FILE="/home/aivault/ai-employee-vault/Logs/health_check.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] Running health check..." >> $LOG_FILE

# Check PM2 processes
PM2_STATUS=$(pm2 status | grep -c "online")
if [ "$PM2_STATUS" -lt 4 ]; then
    echo "[$TIMESTAMP] WARNING: Not all PM2 processes are online" >> $LOG_FILE
    # Send alert email or notification
fi

# Check Odoo
if ! curl -s http://localhost:8069 > /dev/null; then
    echo "[$TIMESTAMP] ERROR: Odoo is not responding" >> $LOG_FILE
    # Restart Odoo
    cd /home/aivault
    docker-compose -f docker-compose-odoo.yml restart
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "[$TIMESTAMP] WARNING: Disk usage at ${DISK_USAGE}%" >> $LOG_FILE
fi

# Check memory
MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.0f", $3/$2*100)}')
if [ "$MEMORY_USAGE" -gt 80 ]; then
    echo "[$TIMESTAMP] WARNING: Memory usage at ${MEMORY_USAGE}%" >> $LOG_FILE
fi

echo "[$TIMESTAMP] Health check complete" >> $LOG_FILE
```

**Make executable and schedule:**

```bash
chmod +x health_check.sh

# Add to crontab (run every 5 minutes)
(crontab -l 2>/dev/null; echo "*/5 * * * * /home/aivault/ai-employee-vault/health_check.sh") | crontab -
```

### Step 6.2: Setup Log Rotation

```bash
sudo nano /etc/logrotate.d/ai-employee
```

**Add:**

```
/home/aivault/ai-employee-vault/Logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0640 aivault aivault
}
```

### Step 6.3: Setup Monitoring Dashboard (Optional)

Install Uptime Kuma for beautiful monitoring:

```bash
# Create directory
mkdir -p /home/aivault/uptime-kuma

# Run with Docker
docker run -d --restart=always \
  -p 3001:3001 \
  -v /home/aivault/uptime-kuma:/app/data \
  --name uptime-kuma \
  louislam/uptime-kuma:1

# Access at: http://your_droplet_ip:3001
```

---

## 🎯 Phase 7: Work-Zone Specialization

### Cloud vs Local Responsibilities

**Cloud Agent (Digital Ocean):**
- ✅ Gmail monitoring & draft responses
- ✅ LinkedIn post creation & scheduling
- ✅ Odoo CRM lead creation (draft)
- ✅ Social media monitoring
- ❌ **NO** WhatsApp session (requires phone)
- ❌ **NO** Banking/payment credentials
- ❌ **NO** Final send/post actions

**Local Agent (Your Laptop):**
- ✅ WhatsApp session & messaging
- ✅ Banking/payment operations
- ✅ Human approval & review
- ✅ Dashboard UI
- ✅ Final execution of approved actions

### Step 7.1: Configure Cloud Mode

Update `.env` on **Cloud Server**:

```bash
CLOUD_MODE=true
LOCAL_MODE=false
DRAFT_ONLY=true
REQUIRE_LOCAL_APPROVAL=true
```

Update `.env` on **Local Machine**:

```bash
CLOUD_MODE=false
LOCAL_MODE=true
DRAFT_ONLY=false
EXECUTE_APPROVED=true
```

### Step 7.2: Setup Approval Workflow

**Cloud creates drafts:**

```python
# In orchestrator.py - cloud mode
if CLOUD_MODE:
    # Create draft approval file
    approval_content = f"""---
type: {action_type}
action: {action}
cloud_draft: true
requires_local_approval: true
---

# Draft Created by Cloud Agent

## Content
{content}

---

## Instructions
This draft was created by the Cloud Agent.
Local agent must review and approve before execution.
"""
```

**Local executes:**

```python
# In execute_approved.py - local mode
if LOCAL_MODE and not CLOUD_MODE:
    # Execute approved actions
    execute_action()
```

---

## 🔄 Phase 8: Vault Sync Setup

### Option 1: Git Sync (Recommended)

**Setup Git Repository:**

```bash
# On LOCAL machine
cd D:\DATA\HACKATHON_0\AI_Employee_Vault
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/ai-vault.git
git push -u origin main
```

**On CLOUD server:**

```bash
cd /home/aivault/ai-employee-vault
git clone https://github.com/yourusername/ai-vault.git .
```

**Setup Auto-Sync Script:**

```bash
cd /home/aivault/ai-employee-vault
nano sync_vault.sh
```

**Add:**

```bash
#!/bin/bash

# Sync vault from Git (Cloud → Local sync)
cd /home/aivault/ai-employee-vault

# Pull latest changes
git pull origin main

# Push cloud updates (drafts, approvals)
git add Needs_Action/ Pending_Approval/ Approved/ Done/
git commit -m "Cloud updates: $(date)"
git push origin main

echo "Vault sync complete: $(date)"
```

**Schedule sync (every 10 minutes):**

```bash
chmod +x sync_vault.sh
(crontab -l 2>/dev/null; echo "*/10 * * * * /home/aivault/ai-employee-vault/sync_vault.sh") | crontab -
```

### Option 2: Syncthing (Real-time Sync)

**Install on both machines:**

```bash
# On Cloud
sudo apt install -y syncthing
syncthing -no-browser
# Access via: http://your_droplet_ip:8384

# On Local (Windows)
# Download from: https://syncthing.net/downloads/
```

**Configure Sync:**

1. Open Syncthing web UI on both machines
2. Add each other as devices (using Device ID)
3. Share folder: `/home/aivault/ai-employee-vault`
4. Set to "Send & Receive" mode
5. **Exclude sensitive files:**
   - `.env`
   - `credentials.json`
   - `*_token.json`
   - `whatsapp_session/`
   - `linkedin_session/`

---

## 🐛 Troubleshooting

### Issue: PM2 Processes Keep Crashing

```bash
# Check logs
pm2 logs orchestrator --lines 100

# Common fixes:
# 1. Check Python path
which python3

# 2. Check virtual environment
source /home/aivault/venv/bin/activate

# 3. Check missing dependencies
pip install -r requirements.txt

# 4. Restart with more memory
pm2 restart orchestrator --max-memory-restart 500M
```

### Issue: Odoo Connection Failed

```bash
# Check if Odoo is running
docker-compose -f docker-compose-odoo.yml ps

# Restart Odoo
docker-compose -f docker-compose-odoo.yml restart

# Check logs
docker-compose -f docker-compose-odoo.yml logs web

# Verify credentials in odoo_server.py
```

### Issue: Gmail API Not Working

```bash
# Re-authenticate
cd /home/aivault/ai-employee-vault
rm gmail_token.json
python gmail_watcher.py
# Follow OAuth flow again
```

### Issue: High Memory Usage

```bash
# Check memory
free -h
htop

# Restart memory-heavy processes
pm2 restart all

# Consider upgrading droplet
# Digital Ocean → Droplets → Resize → 4GB or 8GB
```

### Issue: Disk Space Full

```bash
# Check disk usage
df -h

# Find large files
du -ah /home/aivault | sort -rh | head -20

# Clean old logs
find /home/aivault/ai-employee-vault/Logs -name "*.log" -mtime +7 -delete

# Clean Docker
docker system prune -a
```

---

## 💰 Cost Breakdown

### Monthly Costs (Digital Ocean)

| Resource | Cost | Notes |
|----------|------|-------|
| **Basic Droplet (2GB)** | $12 | Minimum viable |
| **Basic Droplet (4GB)** | $24 | **Recommended** |
| **Backups** | $2.40 | 20% of droplet |
| **Domain** | $1-2 | Optional, prorated |
| **Total (2GB)** | **~$15.40/month** | With backups |
| **Total (4GB)** | **~$27.40/month** | With backups |

### Comparison vs Human Employee

| | Human FTE | AI Employee (Cloud) |
|---|-----------|---------------------|
| **Monthly Cost** | $4,000-8,000 | $27.40 |
| **Hours/Week** | 40 | 168 (24/7) |
| **Availability** | Business hours | Always-on |
| **Consistency** | 85-95% | 99%+ |
| **Setup Time** | 3-6 months | 4 hours |

**ROI:** 99.3% cost savings vs human employee!

---

## ✅ Deployment Checklist

### Pre-Deployment
- [ ] Digital Ocean account created
- [ ] SSH key generated and added
- [ ] Domain purchased (optional)
- [ ] GitHub repository setup
- [ ] Gmail API credentials downloaded
- [ ] Odoo account ready

### Deployment
- [ ] Droplet created (4GB recommended)
- [ ] SSH access verified
- [ ] System packages updated
- [ ] Firewall configured
- [ ] Python virtual environment setup
- [ ] Node.js and PM2 installed
- [ ] Project cloned/uploaded
- [ ] Dependencies installed
- [ ] Environment variables configured
- [ ] Gmail API authenticated
- [ ] Odoo deployed with Docker
- [ ] Odoo apps installed (CRM, Sales, Invoicing)
- [ ] PM2 processes started
- [ ] SSL certificate installed
- [ ] Nginx configured
- [ ] Health checks setup
- [ ] Vault sync configured

### Post-Deployment
- [ ] Test email detection
- [ ] Test draft creation
- [ ] Test Odoo integration
- [ ] Test approval workflow
- [ ] Verify dashboard access
- [ ] Setup monitoring alerts
- [ ] Document credentials securely
- [ ] Test backup restoration

---

## 🎉 Congratulations!

Your AI Employee Vault is now running 24/7 on Digital Ocean!

### What You've Achieved:

✅ **Always-On Automation** - Gmail, LinkedIn monitoring 24/7  
✅ **Cloud Drafts, Local Control** - Secure approval workflow  
✅ **Odoo CRM Integration** - Full business management  
✅ **HTTPS Security** - Professional, encrypted access  
✅ **Health Monitoring** - Auto-recovery from failures  
✅ **Vault Sync** - Cloud ↔ Local coordination  
✅ **Production-Ready** - Backups, logging, monitoring  

### Next Steps:

1. **Monitor for 24 hours** - Ensure stability
2. **Test all workflows** - Email, LinkedIn, Odoo
3. **Setup alerts** - Email/SMS for failures
4. **Document credentials** - Secure password manager
5. **Plan scaling** - Add more watchers as needed

---

## 📞 Support Resources

- **Digital Ocean Docs:** [docs.digitalocean.com](https://docs.digitalocean.com/)
- **Community Forum:** [digitalocean.com/community](https://www.digitalocean.com/community)
- **Project Logs:** `/home/aivault/ai-employee-vault/Logs/`
- **PM2 Monitoring:** `pm2 monit`
- **System Logs:** `journalctl -u nginx`, `journalctl -u docker`

---

**Your Platinum Tier AI Employee is now live! 🚀**

*Total Deployment Time: 3-4 hours*  
*Monthly Cost: ~$27.40*  
*Value: Priceless 24/7 automation!*
