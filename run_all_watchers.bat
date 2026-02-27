@echo off
REM Master Orchestrator - Start All Silver Tier Watchers

echo.
echo ========================================
echo   AI Employee - Silver Tier
echo   Starting All Watchers
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python is not installed
    pause
    exit /b 1
)

echo Starting watchers in separate windows...
echo.

REM Start File Watcher
echo [1/5] Starting File Watcher...
start "File Watcher" python watcher.py
timeout /t 2 /nobreak >nul

REM Start Gmail Watcher
echo [2/5] Starting Gmail Watcher...
start "Gmail Watcher" python gmail_watcher.py
timeout /t 2 /nobreak >nul

REM Start WhatsApp Watcher (Node.js)
echo [3/5] Starting WhatsApp Watcher (Node.js)...
start "WhatsApp Watcher" node whatsapp_watcher_node.js
timeout /t 2 /nobreak >nul

REM Start Approval Checker
echo [4/5] Starting Approval Checker...
start "Approval Checker" python approval_checker.py
timeout /t 2 /nobreak >nul

REM Optional: Start LinkedIn Watcher
REM echo [5/5] Starting LinkedIn Watcher...
REM start "LinkedIn Watcher" python linkedin_watcher.py

echo.
echo ========================================
echo   All Watchers Started!
echo ========================================
echo.
echo Running watchers:
echo   - File Watcher (Inbox monitoring)
echo   - Gmail Watcher (Email monitoring)
echo   - WhatsApp Watcher (Message monitoring)
echo   - Approval Checker (Approval workflow)
echo.
echo To process tasks, tell Claude Code:
echo   "Process tasks in Needs_Action folder"
echo.
echo To stop all watchers:
echo   Close all watcher windows
echo.
pause
