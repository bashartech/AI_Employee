@echo off
REM Scheduler Batch File - Gold Tier
REM Runs the AI Employee Scheduler for weekly CEO briefings

cd /d "%~dp0"

echo ============================================================
echo AI Employee Scheduler - Gold Tier
echo ============================================================
echo.

python scheduler.py

pause
