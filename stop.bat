@echo off
:: ============================================================
:: Face Security Alert System - Stop
:: Gracefully terminates any running instance of the system.
:: ============================================================

title Face Security Alert System - Stop

echo ============================================================
echo  Face Security Alert System - Stopping...
echo ============================================================
echo.

:: Find python processes running run_security_system.py and kill them
tasklist /fi "imagename eq python.exe" 2>nul | find /i "python.exe" >nul
if errorlevel 1 (
    echo  No running Python processes found.
    echo  The system may already be stopped.
    goto :done
)

:: Use wmic to find the specific script and kill it
for /f "tokens=1" %%p in (
    'wmic process where "name='python.exe' and commandline like '%%run_security_system%%'" get processid /format:value 2^>nul ^| find "="'
) do (
    for /f "tokens=2 delims==" %%i in ("%%p") do (
        echo  Stopping process %%i ...
        taskkill /pid %%i /f >nul 2>&1
    )
)

echo  Done. The Face Security Alert System has been stopped.

:done
echo.
echo ============================================================
timeout /t 3 /nobreak >nul
