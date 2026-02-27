@echo off
echo ============================================================
echo WHATSAPP WATCHER
echo ============================================================
echo.
echo This script maintains a persistent WhatsApp connection and:
echo   - Receives incoming WhatsApp messages
echo   - Creates tasks in Needs Action/ folder
echo   - Auto-replies to new contacts (optional)
echo   - Sends queued messages from Send_Queue/ folder
echo.
echo Keep this running for WhatsApp automation to work!
echo.
echo Press Ctrl+C to stop
echo ============================================================
echo.
node whatsapp_watcher_node.js
