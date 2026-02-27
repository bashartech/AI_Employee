@echo off
echo ============================================================
echo AI Employee Vault - Dashboard
echo ============================================================
echo.
echo Starting dashboard server...
echo Dashboard will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

cd dashboard
python app.py

pause
