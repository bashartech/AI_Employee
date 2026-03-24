# 🚀 Quick Start: Digital Ocean Deployment
## Get Your AI Employee Running on Cloud in 4 Hours

**For:** Platinum Tier Deployment  
**Time:** 3-4 hours  
**Cost:** ~$27/month  
**ROI:** 99.3% vs human employee

<!-- scp D:\DATA\HACKATHON_0\AI_Employee_Vault\deploy_digital_ocean.sh root@167.71.237.77:/root/ -->
scp -r D:\DATA\HACKATHON_0\AI_Employee_Vault\* root@167.71.237.77:/home/aivault/ai-employee-vault/
---

## 📦 What You'll Deploy

```
Digital Ocean VM (4GB RAM)
├── Gmail Watcher (24/7 monitoring)
├── LinkedIn Watcher (24/7 posting)
├── Odoo Community (CRM, Invoicing)
├── Cloud Agent (Drafts responses)
└── PM2 (Process management)

Your Laptop (Local)
├── WhatsApp Session
├── Banking/Payments
├── Dashboard & Approval UI
└── Final Execution
```

---

## ⚡ Quick Deploy Steps

### Step 1: Create Digital Ocean Droplet (10 minutes)

1. **Sign up/Login:** [cloud.digitalocean.com](https://cloud.digitalocean.com/)
2. **Create Droplet:**
   - Image: Ubuntu 24.04 LTS
   - Plan: Basic → 4GB RAM ($24/month)
   - Region: Closest to you
   - Add SSH key
   - Enable backups ($2.40/month)
3. **Note your droplet IP:** `YOUR_DROPLET_IP`

### Step 2: Upload Deployment Script (5 minutes)

```bash
# From your local machine (PowerShell or terminal)
scp deploy_digital_ocean.sh root@YOUR_DROPLET_IP:/root/
```

### Step 3: Run Automated Deployment (30 minutes)

```bash
# SSH into droplet
ssh root@YOUR_DROPLET_IP

# Run deployment script
bash /root/deploy_digital_ocean.sh
```

**Script will:**
- ✅ Update system packages
- ✅ Install Python, Node.js, Docker
- ✅ Setup Odoo with Docker
- ✅ Configure firewall
- ✅ Install PM2 process manager
- ✅ Create configuration files
- ✅ Setup health checks

### Step 4: Upload Project Files (10 minutes)

```bash
# From local machine
scp -r D:/DATA/HACKATHON_0/AI_Employee_Vault/* root@YOUR_DROPLET_IP:/home/aivault/ai-employee-vault/

# Upload Gmail credentials
scp credentials.json root@YOUR_DROPLET_IP:/home/aivault/ai-employee-vault/
```

### Step 5: Install Dependencies (15 minutes)

```bash
# On droplet (as aivault user)
ssh aivault@YOUR_DROPLET_IP

cd /home/aivault/ai-employee-vault

# Activate Python environment
source /home/aivault/venv/bin/activate

# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
playwright install-deps chromium

# Install Node packages
npm install
```

### Step 6: Authenticate Gmail (10 minutes)

```bash
# On droplet
cd /home/aivault/ai-employee-vault
source /home/aivault/venv/bin/activate

# Run Gmail watcher (will show OAuth URL)
python gmail_watcher.py
```

1. Copy the URL shown
2. Paste in your LOCAL browser
3. Login to Google
4. Authorize the app
5. Copy the code back to droplet

### Step 7: Configure Odoo (20 minutes)

```bash
# Check Odoo is running
docker-compose -f docker-compose-odoo.yml ps

# Access in browser:
# http://YOUR_DROPLET_IP:8069
```

1. Create database: `ai_employee_db`
2. Install apps: CRM, Sales, Invoicing
3. Create user: `ai@yourcompany.com`
4. Update `mcp_servers/odoo_server.py` with credentials

### Step 8: Start All Services (5 minutes)

<!-- scp -r D:/DATA/HACKATHON_0/AI_Employee_Vault/* root@167.71.237.77:/home/aivault/ai-employee-vault/ -->
<!-- bash /root/deploy_to_digitalocean.sh -->
```bash
cd /home/aivault/ai-employee-vault
source /home/aivault/venv/bin/activate

# Start PM2 processes
pm2 start ecosystem.config.js

# Save PM2 configuration
pm2 save

# Check status
pm2 status
```

scp -i "C:\Users\H P\.ssh\digitaloceonsshkey" token.json root@167.71.237.77:/home/AI_Employee/

scp -i "C:\Users\H P\.ssh\digitaloceonsshkey"  credentials.json root@167.71.237.77:/home/AI_Employee/

**Expected output:**
```
┌────┬─────────────┬────────────┬─────────┬─────────┬──────────┬────────┬──────┬───────────┬──────────┬──────────┐
│ id │ name        │ namespace  │ version │ mode    │ pid      │ uptime │ ↺    │ status    │ cpu      │ mem      │
├────┼─────────────┼────────────┼─────────┼─────────┼──────────┼────────┼──────┼───────────┼──────────┼──────────┤
│ 0  │ orchestrator│ default    │ 1.0.0   │ fork    │ 1234     │ 10s    │ 0    │ online    │ 0%       │ 50mb     │
│ 1  │ execute-app │ default    │ 1.0.0   │ fork    │ 1235     │ 10s    │ 0    │ online    │ 0%       │ 45mb     │
│ 2  │ gmail-watch │ default    │ 1.0.0   │ fork    │ 1236     │ 10s    │ 0    │ online    │ 0%       │ 40mb     │
│ 3  │ dashboard   │ default    │ 1.0.0   │ fork    │ 1237     │ 10s    │ 0    │ online    │ 0%       │ 35mb     │
└────┴─────────────┴────────────┴─────────┴─────────┴──────────┴────────┴──────┴───────────┴──────────┴──────────┘
```

### Step 9: Setup HTTPS (Optional, 10 minutes)

```bash
# If you have a domain:
sudo certbot --nginx -d ai.yourdomain.com

# Update nginx config (see PLATINUM_TIER guide)
```

### Step 10: Test Workflow (15 minutes)

**Test 1: Create manual task**

```bash
# On droplet
cd /home/aivault/ai-employee-vault
nano Needs_Action/test_task.md
```

**Add:**
```markdown
Test task for deployment verification

Please create a LinkedIn post about AI automation.
```

**Test 2: Check orchestrator logs**

```bash
pm2 logs orchestrator --lines 50
```

**Test 3: Check approval file created**

```bash
ls -la Pending_Approval/
```

**Test 4: Access dashboard**

```
http://YOUR_DROPLET_IP:5000
```

---

## 🔧 Post-Deployment Setup

### Setup Git Sync (Cloud ↔ Local)

```bash
# On droplet
cd /home/aivault/ai-employee-vault

# Initialize git
git init
git add .
git commit -m "Initial cloud commit"

# Add your GitHub repo
git remote add origin https://github.com/yourusername/ai-vault.git
git push -u origin main
```

**On local machine:**

```bash
cd D:/DATA/HACKATHON_0/AI_Employee_Vault
git pull origin main
```

### Configure Cloud-Local Split

**On Cloud (`.env`):**
```bash
CLOUD_MODE=true
LOCAL_MODE=false
DRAFT_ONLY=true
```

**On Local (`.env`):**
```bash
CLOUD_MODE=false
LOCAL_MODE=true
EXECUTE_APPROVED=true
```

---

## 📊 Access URLs

| Service | URL | Purpose |
|---------|-----|---------|
| **Dashboard** | `http://YOUR_DROPLET_IP:5000` | Monitor & approve |
| **Odoo** | `http://YOUR_DROPLET_IP:8069` | CRM, invoicing |
| **PM2 Monitor** | `pm2 monit` (SSH) | Process health |

---

## 🔍 Monitoring Commands

```bash
# Check all processes
pm2 status

# View logs
pm2 logs

# Monitor in real-time
pm2 monit

# Check disk space
df -h

# Check memory
free -h
htop


# View health logs
cat /home/aivault/ai-employee-vault/Logs/health_check.log
```

---

## 🆘 Troubleshooting

### Process Crashed

```bash
# Restart all
pm2 restart all

# Restart specific
pm2 restart orchestrator

# Check logs
pm2 logs orchestrator --lines 100
```

### Odoo Not Running

```bash
# Restart Odoo
cd /home/aivault
docker-compose -f docker-compose-odoo.yml restart

# Check logs
docker-compose -f docker-compose-odoo.yml logs -f web
```

### Cannot Access Dashboard

```bash
# Check firewall
sudo ufw status

# Allow port 5000
sudo ufw allow 5000

# Check if running
netstat -tulpn | grep 5000
```

### Gmail API Error

```bash
# Re-authenticate
cd /home/aivault/ai-employee-vault
rm gmail_token.json
python gmail_watcher.py
```

---

## ✅ Success Checklist

- [ ] Droplet created on Digital Ocean
- [ ] All PM2 processes online (green)
- [ ] Odoo accessible at port 8069
- [ ] Dashboard accessible at port 5000
- [ ] Gmail API authenticated
- [ ] Test task created approval file
- [ ] Git sync working
- [ ] Health checks running
- [ ] Firewall configured
- [ ] Backups enabled

---

## 📞 Support Resources

**Documentation:**
- [PLATINUM_TIER_DIGITAL_OCEAN_DEPLOYMENT.md](PLATINUM_TIER_DIGITAL_OCEAN_DEPLOYMENT.md) - Full guide
- [CLOUD_LOCAL_WORK_ZONE_GUIDE.md](CLOUD_LOCAL_WORK_ZONE_GUIDE.md) - Cloud-Local split
- [README.md](README.md) - Project overview

**Digital Ocean:**
- [Droplet Documentation](https://docs.digitalocean.com/products/droplets/)
- [Community Tutorials](https://www.digitalocean.com/community/tutorials)

**Logs:**
- `/home/aivault/ai-employee-vault/Logs/`
- `pm2 logs`
- `docker-compose logs`

---

## 💰 Cost Summary

| Resource | Monthly Cost |
|----------|--------------|
| Digital Ocean (4GB) | $24.00 |
| Backups (20%) | $4.80 |
| **Total** | **$28.80** |

**vs Human Employee:**
- Human: $4,000-8,000/month
- AI Employee: $28.80/month
- **Savings: 99.3%**

---

## 🎉 You're Done!

Your AI Employee is now running 24/7 on Digital Ocean!

**What happens next:**
- Gmail monitored 24/7
- LinkedIn posts drafted automatically
- Odoo CRM ready for leads
- Cloud drafts, Local approves
- You sleep, AI works!

**Next Steps:**
1. Monitor for 24 hours
2. Test all workflows
3. Setup alerts
4. Scale as needed

---

**Welcome to Platinum Tier! 🚀**

*Your AI Employee works while you live.*





 odoo_keywords = ['odoo', 'oddo', 'odo', 'lead', 'crm', 'create lead', 'new lead',
                         'invoice', 'quotation', 'quote', 'customer']
        if any(keyword in content_lower for keyword in odoo_keywords) or 'odoo' in filename_lower:
            # More specific Odoo task detection
            if any(word in content_lower for word in ['lead', 'crm', 'create lead', 'new lead']):
                return 'odoo'
            elif any(word in content_lower for word in ['invoice', 'bill']):
                return 'odoo'
            elif any(word in content_lower for word in ['quotation', 'quote', 'proposal']):
                return 'odoo'
            elif 'odoo' in filename_lower or 'odoo' in content_lower or 'oddo' in content_lower:
                return 'odoo'

        if 'send email' in content_lower or 'send whatsapp' in content_lower:
            return 'inbox_email'

        # Check if it's an inbox file drop
        if 'inbox' in filename_lower or 'source:** inbox' in content_lower:
            # Determine what kind of inbox task - be flexible with spelling
            # First check explicit keywords
            if 'email' in content_lower or 'email' in filename_lower:
                return 'inbox_email'
            elif 'whatsapp' in content_lower or 'whatsapp' in filename_lower or 'watsapp' in filename_lower:
                return 'inbox_whatsapp'
            elif 'linkedin' in content_lower or 'linkedin' in filename_lower:
                return 'inbox_linkedin'