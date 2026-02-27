@echo off
REM Start Claude Code Orchestrator
REM This watches "Needs Action" folder and processes tasks with Claude Code

echo ========================================
echo CLAUDE CODE ORCHESTRATOR
echo ========================================
echo.
echo This will start the orchestrator that:
echo - Watches "Needs Action" folder
echo - Processes tasks with Claude Code
echo - Creates approval files in "Pending Approval"
echo.
echo Make sure you also run:
echo - Watchers (gmail_watcher.py, etc.) to create tasks
echo - execute_approved.py to execute approved tasks
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

python run_automation.py

pause
