#!/bin/bash
# AI Employee Vault - Stop All Services Script

echo "=========================================="
echo "AI EMPLOYEE VAULT - STOPPING ALL SERVICES"
echo "=========================================="
echo ""

# Stop Python processes
echo "🛑 Stopping Orchestrator..."
pkill -f "python.*orchestrator.py"

echo "🛑 Stopping Execute Approved..."
pkill -f "python.*execute_approved.py"

echo "🛑 Stopping Dashboard..."
pkill -f "python.*dashboard.*app.py"

echo "🛑 Stopping Gmail Watcher..."
pkill -f "python.*gmail_watcher.py"

echo "🛑 Stopping WhatsApp Watcher..."
pkill -f "node.*whatsapp_watcher"

# Wait a moment
sleep 2

# Check if any processes are still running
REMAINING=$(ps aux | grep -E "orchestrator|execute_approved|dashboard|gmail_watcher|whatsapp_watcher" | grep -v grep | wc -l)

if [ $REMAINING -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✅ ALL SERVICES STOPPED SUCCESSFULLY"
    echo "=========================================="
else
    echo ""
    echo "⚠️  Some processes may still be running"
    echo "Run: ps aux | grep -E 'orchestrator|execute_approved|dashboard|gmail_watcher|whatsapp_watcher'"
    echo "To force kill: pkill -9 -f 'orchestrator|execute_approved|dashboard|gmail_watcher|whatsapp_watcher'"
fi

echo ""
