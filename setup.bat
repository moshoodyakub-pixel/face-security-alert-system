@echo off
:: ============================================================
:: Face Security Alert System - One-Time Setup
:: Run this script once after cloning the repository.
:: ============================================================

title Face Security Alert System - Setup

echo ============================================================
echo  Face Security Alert System - Setup
echo ============================================================
echo.

:: Check Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+ from https://python.org
    echo         Make sure to tick "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [1/4] Python found:
python --version
echo.

:: Create virtual environment
echo [2/4] Creating virtual environment...
if exist venv (
    echo        Virtual environment already exists, skipping.
) else (
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo        Virtual environment created.
)
echo.

:: Activate and install dependencies
echo [3/4] Installing dependencies (this may take several minutes)...
call venv\Scripts\activate.bat
pip install --upgrade pip --quiet
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)
echo        Dependencies installed.
echo.

:: Create .env file from example if it does not exist
echo [4/4] Setting up environment configuration...
if not exist .env (
    copy .env.example .env >nul
    echo        Created .env from .env.example
    echo        Edit .env with your Telegram credentials if desired.
) else (
    echo        .env already exists, skipping.
)
echo.

echo ============================================================
echo  Setup complete!
echo.
echo  Next steps:
echo    1. Add face photos:  python scripts\add_new_person.py
echo    2. Build database:   python scripts\train_known_faces.py
echo    3. Start the system: double-click  start.bat
echo.
echo  To create desktop shortcuts run:  create_shortcuts.bat
echo ============================================================
echo.
pause
