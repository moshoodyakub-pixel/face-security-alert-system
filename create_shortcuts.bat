@echo off
:: ============================================================
:: Face Security Alert System - Create Desktop Shortcuts
:: Run this once to place Start and Stop shortcuts on your
:: Windows Desktop.
:: ============================================================

title Face Security Alert System - Create Shortcuts

cd /d "%~dp0"
set "APP_DIR=%~dp0"
:: Remove trailing backslash
if "%APP_DIR:~-1%"=="\" set "APP_DIR=%APP_DIR:~0,-1%"

set "DESKTOP=%USERPROFILE%\Desktop"
set "START_LNK=%DESKTOP%\Face Security - Start.lnk"
set "STOP_LNK=%DESKTOP%\Face Security - Stop.lnk"

echo ============================================================
echo  Creating desktop shortcuts...
echo ============================================================
echo.

:: ---- Start shortcut ----
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell; ^
   $s  = $ws.CreateShortcut('%START_LNK%'); ^
   $s.TargetPath      = '%APP_DIR%\start.bat'; ^
   $s.WorkingDirectory= '%APP_DIR%'; ^
   $s.WindowStyle     = 1; ^
   $s.Description     = 'Start Face Security Alert System'; ^
   $s.Save()"

if exist "%START_LNK%" (
    echo  [OK] Start shortcut created: %START_LNK%
) else (
    echo  [ERROR] Could not create Start shortcut.
)

:: ---- Stop shortcut ----
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ws = New-Object -ComObject WScript.Shell; ^
   $s  = $ws.CreateShortcut('%STOP_LNK%'); ^
   $s.TargetPath      = '%APP_DIR%\stop.bat'; ^
   $s.WorkingDirectory= '%APP_DIR%'; ^
   $s.WindowStyle     = 1; ^
   $s.Description     = 'Stop Face Security Alert System'; ^
   $s.Save()"

if exist "%STOP_LNK%" (
    echo  [OK] Stop  shortcut created: %STOP_LNK%
) else (
    echo  [ERROR] Could not create Stop shortcut.
)

echo.
echo ============================================================
echo  Done! Look for the shortcuts on your Desktop:
echo    "Face Security - Start.lnk"
echo    "Face Security - Stop.lnk"
echo ============================================================
echo.
pause
