@echo off
:: ============================================================
:: Face Security Alert System - Start
:: Double-click (or use the desktop shortcut) to start.
:: ============================================================

title Face Security Alert System - Running

:: Change to the script's own directory so relative paths work
cd /d "%~dp0"

:: Make sure the virtual environment exists
if not exist venv\Scripts\activate.bat (
    echo [ERROR] Virtual environment not found.
    echo         Please run setup.bat first.
    pause
    exit /b 1
)

:: Activate virtual environment
call venv\Scripts\activate.bat

echo ============================================================
echo  Face Security Alert System - Starting...
echo  Press Q in the video window  OR  Ctrl+C here to stop.
echo ============================================================
echo.

python scripts\run_security_system.py

echo.
echo ============================================================
echo  System stopped.
echo ============================================================
pause
