@echo off
title WoWOBSAutoClip Lite Launcher
set SCRIPT_NAME=%WoWOBSAutoClip Lite.py

:: Use a clean, subtle color (Cyan)
color 0B

echo.
echo  --------------------------------------------------
echo    	W o W   O B S   A u t o C l i p
echo    [ Raids  -  Mythic+  -  Retail  -  Classic  ]
echo  --------------------------------------------------
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
echo [SUCCESS] Monitoring WoW Logs...
echo (Keep this window open while playing!)
echo.
python "%SCRIPT_NAME%"

pause