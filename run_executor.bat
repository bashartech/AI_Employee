@echo off
echo ============================================================
echo APPROVED ACTIONS EXECUTOR
echo ============================================================
echo.
echo This script watches the Approved folder and automatically:
echo   - Sends emails from approved email requests
echo   - Sends WhatsApp messages from approved WhatsApp requests
echo   - Posts LinkedIn posts from approved LinkedIn requests
echo.
echo Move approval files to the "Approved" folder to execute them.
echo.
echo Press Ctrl+C to stop
echo ============================================================
echo.
python execute_approved.py
