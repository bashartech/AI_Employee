#!/bin/bash
# AI Employee Vault - Quick Start Script
# Starts all automation components

echo "=========================================="
echo "AI EMPLOYEE VAULT - STARTING ALL SERVICES"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "⚠️  Node.js not found. WhatsApp automation will not work."
fi

# Check if Docker is running (for Odoo)
if ! docker ps &> /dev/null; then
    echo "⚠️  Docker not running. Odoo integration will not work."
else
    echo "✅ Docker is running"
    # Start Odoo container if exists
    if docker ps -a | grep -q oddo; then
        echo "🚀 Starting Odoo container..."
        docker start oddo
    fi
fi

echo ""
echo "Starting components..."
echo ""

# Create logs directory
mkdir -p logs

# Start Orchestrator in background
echo "🤖 Starting Orchestrator..."
python engine/orchestrator.py > logs/orchestrator.log 2>&1 &
ORCHESTRATOR_PID=$!
echo "   PID: $ORCHESTRATOR_PID"

# Wait a moment
sleep 2

# Start Execute Approved in background
echo "⚡ Starting Execute Approved..."
python execute_approved.py > logs/execute_approved.log 2>&1 &
EXECUTE_PID=$!
echo "   PID: $EXECUTE_PID"

# Wait a moment
sleep 2

# Start Dashboard in background
echo "📊 Starting Dashboard..."
cd dashboard
python app.py > ../logs/dashboard.log 2>&1 &
DASHBOARD_PID=$!
cd ..
echo "   PID: $DASHBOARD_PID"

# Wait a moment
sleep 2

# Start Gmail Watcher (optional)
echo "📧 Starting Gmail Watcher (optional)..."
python gmail_watcher.py > logs/gmail_watcher.log 2>&1 &
GMAIL_PID=$!
echo "   PID: $GMAIL_PID"

# Start WhatsApp Watcher (optional, if Node.js available)
if command -v node &> /dev/null; then
    echo "💬 Starting WhatsApp Watcher (optional)..."
    node whatsapp_watcher_node.js > logs/whatsapp_watcher.log 2>&1 &
    WHATSAPP_PID=$!
    echo "   PID: $WHATSAPP_PID"
fi

echo ""
echo "=========================================="
echo "✅ ALL SERVICES STARTED"
echo "=========================================="
echo ""
echo "📊 Dashboard: http://localhost:5000"
echo "🏢 Odoo CRM: http://localhost:8069"
echo ""
echo "Process IDs:"
echo "  Orchestrator: $ORCHESTRATOR_PID"
echo "  Execute Approved: $EXECUTE_PID"
echo "  Dashboard: $DASHBOARD_PID"
echo "  Gmail Watcher: $GMAIL_PID"
if [ ! -z "$WHATSAPP_PID" ]; then
    echo "  WhatsApp Watcher: $WHATSAPP_PID"
fi
echo ""
echo "Logs location: logs/"
echo ""
echo "To stop all services, run: ./stop_all.sh"
echo "Or press Ctrl+C and run: pkill -f 'orchestrator|execute_approved|dashboard|gmail_watcher|whatsapp_watcher'"
echo ""
echo "=========================================="
echo "Ready to process tasks! 🚀"
echo "=========================================="
