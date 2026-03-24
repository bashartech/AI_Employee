#!/bin/bash

# ============================================================================
# AI Employee Vault - Complete Digital Ocean Deployment Script
# For: https://github.com/bashartech/AI_Employee
# ============================================================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "=========================================================="
echo "  AI Employee Vault - Digital Ocean Deployment"
echo "  GitHub: https://github.com/bashartech/AI_Employee"
echo "=========================================================="
echo -e "${NC}"
echo ""

# ============================================================================
# STEP 1: System Update
# ============================================================================
echo -e "${GREEN}[Step 1/12] Updating system packages...${NC}"
apt update && apt upgrade -y
echo -e "${GREEN}✓ System updated${NC}"
echo ""

# ============================================================================
# STEP 2: Install Dependencies
# ============================================================================
echo -e "${GREEN}[Step 2/12] Installing dependencies...${NC}"
apt install -y \
    git \
    curl \
    wget \
    vim \
    htop \
    ufw \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    nodejs \
    npm \
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

echo -e "${GREEN}✓ Dependencies installed${NC}"
echo ""

# ============================================================================
# STEP 3: Clone GitHub Repository
# ============================================================================
echo -e "${GREEN}[Step 3/12] Cloning GitHub repository...${NC}"
cd /home
git clone https://github.com/bashartech/AI_Employee.git
cd AI_Employee
echo -e "${GREEN}✓ Repository cloned${NC}"
echo ""

# ============================================================================
# STEP 4: Create Folders
# ============================================================================
echo -e "${GREEN}[Step 4/12] Creating folder structure...${NC}"
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
    odoo/config \
    odoo/addons
echo -e "${GREEN}✓ Folders created${NC}"
echo ""

# ============================================================================
# STEP 5: Setup Python Virtual Environment
# ============================================================================
echo -e "${GREEN}[Step 5/12] Setting up Python virtual environment...${NC}"
python3 -m venv /home/venv
source /home/venv/bin/activate
pip install --upgrade pip
echo -e "${GREEN}✓ Python environment created${NC}"
echo ""

# ============================================================================
# STEP 6: Install Python Dependencies
# ============================================================================
echo -e "${GREEN}[Step 6/12] Installing Python dependencies...${NC}"
cd /home/AI_Employee
pip install -r requirements.txt
echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo ""

# ============================================================================
# STEP 7: Install Playwright
# ============================================================================
echo -e "${GREEN}[Step 7/12] Installing Playwright browsers...${NC}"
playwright install chromium
playwright install-deps chromium
echo -e "${GREEN}✓ Playwright installed${NC}"
echo ""

# ============================================================================
# STEP 8: Install Node.js Dependencies
# ============================================================================
echo -e "${GREEN}[Step 8/12] Installing Node.js dependencies...${NC}"
cd /home/AI_Employee
npm install
npm install -g pm2
echo -e "${GREEN}✓ Node.js dependencies installed${NC}"
echo ""

# ============================================================================
# STEP 9: Create .env File
# ============================================================================
echo -e "${GREEN}[Step 9/12] Creating .env configuration...${NC}"
cd /home/AI_Employee
cat > .env << 'EOF'
# AI Configuration
QWEN_BASE_URL=http://localhost:11434/v1
QWEN_API_KEY=dummy-key
QWEN_MODEL=qwen2.5:latest

# Gmail API Configuration
GMAIL_CREDENTIALS_PATH=/home/AI_Employee/credentials.json
GMAIL_TOKEN_PATH=/home/AI_Employee/gmail_token.json

# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee_db
ODOO_USERNAME=ai@bashartech.com
ODOO_PASSWORD=YourOdooPassword123

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
echo -e "${GREEN}✓ .env file created${NC}"
echo -e "${YELLOW}⚠️  Note: Update .env with your actual credentials later${NC}"
echo ""

# ============================================================================
# STEP 10: Setup Odoo with Docker
# ============================================================================
echo -e "${GREEN}[Step 10/12] Setting up Odoo with Docker...${NC}"
cd /home/AI_Employee
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
echo -e "${GREEN}✓ Odoo setup complete${NC}"
echo -e "${YELLOW}⏳ Waiting for Odoo to start (30 seconds)...${NC}"
sleep 30
echo -e "${GREEN}✓ Odoo should be running now${NC}"
echo ""

# ============================================================================
# STEP 11: Configure Firewall
# ============================================================================
echo -e "${GREEN}[Step 11/12] Configuring firewall...${NC}"
ufw allow OpenSSH
ufw allow http
ufw allow https
ufw allow 8069
ufw allow 5000
echo "y" | ufw enable
echo -e "${GREEN}✓ Firewall configured${NC}"
echo ""

# ============================================================================
# STEP 12: Create PM2 Ecosystem File
# ============================================================================
echo -e "${GREEN}[Step 12/12] Creating PM2 ecosystem configuration...${NC}"
cd /home/AI_Employee
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [
    {
      name: 'orchestrator',
      script: 'python3',
      args: 'engine/orchestrator.py',
      cwd: '/home/AI_Employee',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
        PATH: '/home/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
      },
      error_file: '/home/AI_Employee/Logs/orchestrator.err',
      out_file: '/home/AI_Employee/Logs/orchestrator.out',
      log_file: '/home/AI_Employee/Logs/orchestrator.log',
      time: true,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s'
    },
    {
      name: 'execute-approved',
      script: 'python3',
      args: 'execute_approved.py',
      cwd: '/home/AI_Employee',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
        PATH: '/home/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
      },
      error_file: '/home/AI_Employee/Logs/execute_approved.err',
      out_file: '/home/AI_Employee/Logs/execute_approved.out',
      log_file: '/home/AI_Employee/Logs/execute_approved.log',
      time: true,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s'
    },
    {
      name: 'gmail-watcher',
      script: 'python3',
      args: 'gmail_watcher.py',
      cwd: '/home/AI_Employee',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
        PATH: '/home/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
      },
      error_file: '/home/AI_Employee/Logs/gmail_watcher.err',
      out_file: '/home/AI_Employee/Logs/gmail_watcher.out',
      log_file: '/home/AI_Employee/Logs/gmail_watcher.log',
      time: true,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s'
    },
    {
      name: 'dashboard',
      script: 'python3',
      args: 'dashboard/app.py',
      cwd: '/home/AI_Employee',
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
        PORT: '5000',
        PATH: '/home/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
      },
      error_file: '/home/AI_Employee/Logs/dashboard.err',
      out_file: '/home/AI_Employee/Logs/dashboard.out',
      log_file: '/home/AI_Employee/Logs/dashboard.log',
      time: true,
      autorestart: true,
      max_restarts: 10,
      min_uptime: '10s'
    }
  ]
};
EOF
echo -e "${GREEN}✓ PM2 configuration created${NC}"
echo ""

# ============================================================================
# COMPLETE - Show Next Steps
# ============================================================================
echo -e "${BLUE}"
echo "=========================================================="
echo "  ✅ AUTOMATED DEPLOYMENT COMPLETE!"
echo "=========================================================="
echo -e "${NC}"
echo ""
echo -e "${YELLOW}📋 NEXT STEPS (You must do these manually):${NC}"
echo ""
echo "1. Upload Gmail credentials.json:"
echo -e "   ${GREEN}scp -i \"C:\\Users\\H P\\.ssh\\digitaloceonsshkey\" D:\\DATA\\HACKATHON_0\\AI_Employee_Vault\\credentials.json root@167.71.237.77:/home/AI_Employee/${NC}"
echo ""
echo "2. Authenticate Gmail API:"
echo -e "   ${GREEN}cd /home/AI_Employee && source /home/venv/bin/activate && python gmail_watcher.py${NC}"
echo "   (Follow the OAuth URL in your browser)"
echo ""
echo "3. Configure Odoo (in browser):"
echo -e "   ${GREEN}http://167.71.237.77:8069${NC}"
echo "   - Create database: ai_employee_db"
echo "   - Install apps: CRM, Sales, Invoicing"
echo "   - Update mcp_servers/odoo_server.py with credentials"
echo ""
echo "4. Start all services:"
echo -e "   ${GREEN}cd /home/AI_Employee && source /home/venv/bin/activate && pm2 start ecosystem.config.js && pm2 save${NC}"
echo ""
echo "5. Setup PM2 startup:"
echo -e "   ${GREEN}pm2 startup${NC}"
echo "   (Copy and run the command it shows)"
echo ""
echo "6. Access Dashboard:"
echo -e "   ${GREEN}http://167.71.237.77:5000${NC}"
echo ""
echo -e "${YELLOW}📊 Useful Commands:${NC}"
echo "   - Check status: pm2 status"
echo "   - View logs: pm2 logs"
echo "   - Monitor: pm2 monit"
echo "   - Restart all: pm2 restart all"
echo ""
echo -e "${BLUE}=========================================================="
echo ""
