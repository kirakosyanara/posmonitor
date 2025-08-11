@echo off
REM POS Monitor Service Installation Script
REM Run as Administrator

echo.
echo ============================================
echo POS Monitor Service Installation
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

REM Check if Python is available
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8 or higher
    pause
    exit /b 1
)

echo [1/5] Creating directories...
if not exist "C:\ProgramData\POSMonitor" mkdir "C:\ProgramData\POSMonitor"
if not exist "C:\ProgramData\POSMonitor\logs" mkdir "C:\ProgramData\POSMonitor\logs"

echo [2/5] Copying configuration file...
if exist "pos-monitor-config.json" (
    copy /Y "pos-monitor-config.json" "C:\ProgramData\POSMonitor\pos-monitor-config.json"
    echo Configuration file copied to C:\ProgramData\POSMonitor\
) else (
    echo WARNING: pos-monitor-config.json not found in current directory
    echo Please create the configuration file manually
)

echo [3/5] Installing Python dependencies...
pip install -r pos-monitor-requirements.txt
if %errorLevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/5] Installing Windows service...
python pos-monitor-service.py install
if %errorLevel% neq 0 (
    echo ERROR: Failed to install service
    pause
    exit /b 1
)

echo [5/5] Setting service permissions...
REM Grant service account permissions to log directory
icacls "C:\ProgramData\POSMonitor" /grant "NT AUTHORITY\SYSTEM:(OI)(CI)F" /T >nul 2>&1

echo.
echo ============================================
echo Installation Complete!
echo ============================================
echo.
echo The POS Monitor service has been installed successfully.
echo.
echo To start the service now, run:
echo   net start POSMonitor
echo.
echo To configure the service, edit:
echo   C:\ProgramData\POSMonitor\pos-monitor-config.json
echo.
echo The service will start automatically on system boot.
echo.

choice /C YN /M "Would you like to start the service now"
if %errorLevel% equ 1 (
    echo Starting POS Monitor service...
    net start POSMonitor
    if %errorLevel% equ 0 (
        echo Service started successfully!
    ) else (
        echo ERROR: Failed to start service. Check the logs for details.
    )
)

pause