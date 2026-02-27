@echo off
REM Claude Code Orchestrator Launcher
REM Starts Claude Code automation for AI Employee Vault

cd /d "%~dp0"

echo ============================================================
echo CLAUDE CODE ORCHESTRATOR - AI Employee Vault
echo ============================================================
echo.
echo Starting Claude Code automation...
echo.
echo This will:
echo   1. Watch Needs Action folder for new tasks
echo   2. Automatically trigger Claude Code to process them
echo   3. Create approval files when needed
echo   4. Move completed tasks to Done folder
echo.
echo Press Ctrl+C to stop
echo ============================================================
echo.

REM Check if Claude Code is installed
where claude >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Claude Code (claude) is not installed or not in PATH
    echo.
    echo Please install Claude Code:
    echo   npm install -g @anthropic-ai/claude-code
    echo.
    echo Or use the Claude Code Router for free tier
    echo.
    pause
    exit /b 1
)

REM Check if authenticated
claude --version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Claude Code is not authenticated
    echo.
    echo Please run: claude login
    echo.
    pause
    exit /b 1
)

echo Starting Claude Code Orchestrator...
echo.

REM Start the orchestrator
python claude_orchestrator.py

pause
