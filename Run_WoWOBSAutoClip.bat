@echo off
title WoWOBSAutoClip Launcher
set SCRIPT_NAME=WoWOBSAutoClip.py

echo ============================================
echo      WoWOBSAutoClip - Automated Raid Recorder
echo ============================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    echo Please install Python from https://www.python.org/
    pause
    exit /b
)

:: Try to import the library; if it fails, install it
python -c "import obswebsocket" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] obs-websocket-py library not found. Installing now...
    pip install obs-websocket-py
)

:: Run the script
echo [SUCCESS] Launching %SCRIPT_NAME%...
echo (Keep this window open while raiding!)
echo.
python %SCRIPT_NAME%

pause