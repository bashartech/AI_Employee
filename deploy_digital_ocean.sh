#!/bin/bash

# ============================================================================
# AI Employee Vault - Digital Ocean Automated Deployment Script
# ============================================================================
# This script automates the entire deployment process on Digital Ocean
# Usage: bash deploy_digital_ocean.sh
# ============================================================================

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="ai-employee-vault"
INSTALL_DIR="/home/aivault/${PROJECT_NAME}"
VENV_DIR="/home/aivault/venv"
ODOO_VERSION="17.0"

echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}AI Employee Vault - Digital Ocean Deployment${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""

# Check if running as root
if [ "$EUID" -eq 0 ]; then
    echo -e "${YELLOW}Warning: Running as root. Consider running as aivault user.${NC}"
fi

# ============================================================================
# Phase 1: System Update & Package Installation
# ============================================================================
echo -e "${GREEN}[Phase 1/8] Updating system packages...${NC}"
apt update && apt upgrade -y

echo -e "${GREEN}[Phase 1/8] Installing essential packages...${NC}"
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
    docker-compose \
    build-essential \
    libjpeg-dev \
    zlib1g-dev \
    libpng-dev \
    libxml2-dev \
    libxslt1-dev \
    libffi-dev \
    libssl-dev

echo -e "${GREEN}✓ System packages installed${NC}"
echo ""

# ============================================================================
# Phase 2: Python & Node.js Setup
# ============================================================================
echo -e "${GREEN}[Phase 2/8] Setting up Python virtual environment...${NC}"

# Create virtual environment
python3 -m venv ${VENV_DIR}
source ${VENV_DIR}/bin/activate

# Upgrade pip
pip install --upgrade pip

echo -e "${GREEN}✓ Python environment setup complete${NC}"
echo ""

# ============================================================================
# Phase 3: Project Directory Setup
# ============================================================================
echo -e "${GREEN}[Phase 3/8] Creating project directories...${NC}"

mkdir -p ${INSTALL_DIR}
cd ${INSTALL_DIR}

# Create folder structure
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
    dashboard \
    odoo/config \
    odoo/addons

echo -e "${GREEN}✓ Directory structure created${NC}"
echo ""

# ============================================================================
# Phase 4: Docker & Odoo Setup
# ============================================================================
echo -e "${GREEN}[Phase 4/8] Setting up Odoo with Docker...${NC}"

# Create docker-compose file
cat > docker-compose-odoo.yml << 'EOF'
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
EOF

# Start Odoo
docker-compose -f docker-compose-odoo.yml up -d

echo -e "${GREEN}✓ Odoo container started${NC}"
echo ""

# ============================================================================
# Phase 5: Firewall Configuration
# ============================================================================
echo -e "${GREEN}[Phase 5/8] Configuring firewall...${NC}"

# Setup UFW
ufw allow OpenSSH
ufw allow http
ufw allow https
ufw allow 8069
ufw allow 5000

# Enable firewall (comment out if running remotely to avoid lockout)
echo "y" | ufw enable

echo -e "${GREEN}✓ Firewall configured${NC}"
echo ""

# ============================================================================
# Phase 6: PM2 Installation
# ============================================================================
echo -e "${GREEN}[Phase 6/8] Installing PM2 process manager...${NC}"

# Install PM2 globally
npm install -g pm2

# Setup PM2 startup
pm2 startup systemd -u aivault --hp /home/aivault

echo -e "${GREEN}✓ PM2 installed${NC}"
echo ""

# ============================================================================
# Phase 7: Create Configuration Files
# ============================================================================
echo -e "${GREEN}[Phase 7/8] Creating configuration files...${NC}"

# Create .env file
cat > .env << 'EOF'
# AI Configuration
QWEN_BASE_URL=http://localhost:11434/v1
QWEN_API_KEY=dummy-key
QWEN_MODEL=qwen2.5:latest

# Or use Claude API
# ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Gmail API Configuration
GMAIL_CREDENTIALS_PATH=/home/aivault/ai-employee-vault/credentials.json
GMAIL_TOKEN_PATH=/home/aivault/ai-employee-vault/gmail_token.json

# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee_db
ODOO_USERNAME=ai@yourcompany.com
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
DRAFT_ONLY=true
REQUIRE_LOCAL_APPROVAL=true
EOF

# Create PM2 ecosystem file
cat > ecosystem.config.js << 'EOF'
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
EOF

# Create health check script
cat > health_check.sh << 'EOF'
#!/bin/bash

LOG_FILE="/home/aivault/ai-employee-vault/Logs/health_check.log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] Running health check..." >> $LOG_FILE

# Check PM2 processes
PM2_STATUS=$(pm2 status | grep -c "online" || echo "0")
if [ "$PM2_STATUS" -lt 4 ]; then
    echo "[$TIMESTAMP] WARNING: Not all PM2 processes are online" >> $LOG_FILE
fi

# Check Odoo
if ! curl -s http://localhost:8069 > /dev/null; then
    echo "[$TIMESTAMP] ERROR: Odoo is not responding" >> $LOG_FILE
    cd /home/aivault
    docker-compose -f docker-compose-odoo.yml restart
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 80 ]; then
    echo "[$TIMESTAMP] WARNING: Disk usage at ${DISK_USAGE}%" >> $LOG_FILE
fi

echo "[$TIMESTAMP] Health check complete" >> $LOG_FILE
EOF

chmod +x health_check.sh

echo -e "${GREEN}✓ Configuration files created${NC}"
echo ""

# ============================================================================
# Phase 8: Final Instructions
# ============================================================================
echo -e "${GREEN}[Phase 8/8] Deployment complete!${NC}"
echo ""
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}✅ DEPLOYMENT COMPLETE!${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo ""
echo "1. Upload your project files:"
echo -e "   ${GREEN}scp -r /local/path/AI_Employee_Vault/* aivault@YOUR_DROPLET_IP:${INSTALL_DIR}/${NC}"
echo ""
echo "2. Upload Gmail credentials:"
echo -e "   ${GREEN}scp credentials.json aivault@YOUR_DROPLET_IP:${INSTALL_DIR}/${NC}"
echo ""
echo "3. Install Python dependencies:"
echo -e "   ${GREEN}cd ${INSTALL_DIR} && source ${VENV_DIR}/bin/activate && pip install -r requirements.txt${NC}"
echo ""
echo "4. Install Playwright browsers:"
echo -e "   ${GREEN}playwright install chromium && playwright install-deps chromium${NC}"
echo ""
echo "5. Install Node.js dependencies:"
echo -e "   ${GREEN}cd ${INSTALL_DIR} && npm install${NC}"
echo ""
echo "6. Authenticate Gmail:"
echo -e "   ${GREEN}cd ${INSTALL_DIR} && source ${VENV_DIR}/bin/activate && python gmail_watcher.py${NC}"
echo ""
echo "7. Start all services:"
echo -e "   ${GREEN}cd ${INSTALL_DIR} && source ${VENV_DIR}/bin/activate && pm2 start ecosystem.config.js && pm2 save${NC}"
echo ""
echo "8. Setup SSL certificate (optional):"
echo -e "   ${GREEN}certbot --nginx -d your-domain.com${NC}"
echo ""
echo -e "${YELLOW}Access URLs:${NC}"
echo "  - Dashboard: http://YOUR_DROPLET_IP:5000"
echo "  - Odoo: http://YOUR_DROPLET_IP:8069"
echo ""
echo -e "${YELLOW}Useful Commands:${NC}"
echo "  - Check status: pm2 status"
echo "  - View logs: pm2 logs"
echo "  - Monitor: pm2 monit"
echo "  - Restart all: pm2 restart all"
echo ""
echo -e "${BLUE}================================================${NC}"
echo ""
