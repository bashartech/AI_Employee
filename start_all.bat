@echo off
REM AI Employee Vault - Quick Start Script (Windows)
REM Starts all automation components

echo ==========================================
echo AI EMPLOYEE VAULT - STARTING ALL SERVICES
echo ==========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo X Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo ! Node.js not found. WhatsApp automation will not work.
)

REM Check if Docker is running (for Odoo)
docker ps >nul 2>&1
if errorlevel 1 (
    echo ! Docker not running. Odoo integration will not work.
) else (
    echo √ Docker is running
    REM Start Odoo container if exists
    docker ps -a | findstr oddo >nul 2>&1
    if not errorlevel 1 (
        echo Starting Odoo container...
        docker start oddo
    )
)

echo.
echo Starting components...
echo.

REM Create logs directory
if not exist logs mkdir logs

REM Start Orchestrator
echo Starting Orchestrator...
start "AI Employee - Orchestrator" /MIN cmd /c "python engine/orchestrator.py > logs/orchestrator.log 2>&1"
timeout /t 2 /nobreak >nul

REM Start Execute Approved
echo Starting Execute Approved...
start "AI Employee - Execute Approved" /MIN cmd /c "python execute_approved.py > logs/execute_approved.log 2>&1"
timeout /t 2 /nobreak >nul

REM Start Dashboard
echo Starting Dashboard...
start "AI Employee - Dashboard" /MIN cmd /c "cd dashboard && python app.py > ../logs/dashboard.log 2>&1"
timeout /t 3 /nobreak >nul

REM Start Gmail Watcher (optional)
echo Starting Gmail Watcher (optional)...
start "AI Employee - Gmail Watcher" /MIN cmd /c "python gmail_watcher.py > logs/gmail_watcher.log 2>&1"
timeout /t 2 /nobreak >nul

REM Start WhatsApp Watcher (optional, if Node.js available)
node --version >nul 2>&1
if not errorlevel 1 (
    echo Starting WhatsApp Watcher (optional)...
    start "AI Employee - WhatsApp Watcher" /MIN cmd /c "node whatsapp_watcher_node.js > logs/whatsapp_watcher.log 2>&1"
)

echo.
echo ==========================================
echo √ ALL SERVICES STARTED
echo ==========================================
echo.
echo Dashboard: http://localhost:5000
echo Odoo CRM: http://localhost:8069
echo.
echo All services are running in minimized windows.
echo Logs location: logs/
echo.
echo To stop all services, run: stop_all.bat
echo Or close all "AI Employee" windows from taskbar
echo.
echo ==========================================
echo Ready to process tasks!
echo ==========================================
echo.

REM Open dashboard in browser
timeout /t 3 /nobreak >nul
start http://localhost:5000

pause
