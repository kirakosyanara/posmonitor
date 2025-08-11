@echo off
REM POS Monitor Service Uninstallation Script
REM Run as Administrator

echo.
echo ============================================
echo POS Monitor Service Uninstallation
echo ============================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

REM Change to script directory
cd /d %~dp0

echo This will uninstall the POS Monitor service and optionally remove all data.
echo.
choice /C YN /M "Are you sure you want to continue"
if %errorLevel% neq 1 (
    echo Uninstallation cancelled.
    pause
    exit /b 0
)

echo.
echo [1/3] Stopping service if running...
net stop POSMonitor >nul 2>&1
if %errorLevel% equ 0 (
    echo Service stopped successfully
) else (
    echo Service was not running
)

echo [2/3] Uninstalling Windows service...
python pos-monitor-service.py remove
if %errorLevel% neq 0 (
    echo WARNING: Failed to uninstall service via Python
    echo Attempting to remove using SC command...
    sc delete POSMonitor
)

echo [3/3] Service uninstalled
echo.

choice /C YN /M "Would you like to remove all POS Monitor data and logs"
if %errorLevel% equ 1 (
    echo Removing POS Monitor data...
    if exist "C:\ProgramData\POSMonitor" (
        rmdir /S /Q "C:\ProgramData\POSMonitor"
        echo Data directory removed
    )
) else (
    echo Data and logs preserved at C:\ProgramData\POSMonitor\
)

echo.
echo ============================================
echo Uninstallation Complete!
echo ============================================
echo.
echo The POS Monitor service has been removed.
echo.

pause