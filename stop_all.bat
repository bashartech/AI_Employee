@echo off
REM AI Employee Vault - Stop All Services Script (Windows)

echo ==========================================
echo AI EMPLOYEE VAULT - STOPPING ALL SERVICES
echo ==========================================
echo.

echo Stopping Orchestrator...
taskkill /FI "WINDOWTITLE eq AI Employee - Orchestrator*" /F >nul 2>&1

echo Stopping Execute Approved...
taskkill /FI "WINDOWTITLE eq AI Employee - Execute Approved*" /F >nul 2>&1

echo Stopping Dashboard...
taskkill /FI "WINDOWTITLE eq AI Employee - Dashboard*" /F >nul 2>&1

echo Stopping Gmail Watcher...
taskkill /FI "WINDOWTITLE eq AI Employee - Gmail Watcher*" /F >nul 2>&1

echo Stopping WhatsApp Watcher...
taskkill /FI "WINDOWTITLE eq AI Employee - WhatsApp Watcher*" /F >nul 2>&1

REM Also kill by process name as backup
taskkill /FI "IMAGENAME eq python.exe" /FI "COMMANDLINE eq *orchestrator*" /F >nul 2>&1
taskkill /FI "IMAGENAME eq python.exe" /FI "COMMANDLINE eq *execute_approved*" /F >nul 2>&1
taskkill /FI "IMAGENAME eq python.exe" /FI "COMMANDLINE eq *dashboard*" /F >nul 2>&1
taskkill /FI "IMAGENAME eq python.exe" /FI "COMMANDLINE eq *gmail_watcher*" /F >nul 2>&1
taskkill /FI "IMAGENAME eq node.exe" /FI "COMMANDLINE eq *whatsapp_watcher*" /F >nul 2>&1

timeout /t 2 /nobreak >nul

echo.
echo ==========================================
echo √ ALL SERVICES STOPPED
echo ==========================================
echo.
echo All AI Employee Vault services have been stopped.
echo.

pause
