@echo off
REM Test Odoo Connection
REM Quick test to verify Odoo MCP server is working

cd /d "%~dp0"

echo ============================================================
echo Testing Odoo MCP Server Connection
echo ============================================================
echo.

python test_odoo.py

pause
