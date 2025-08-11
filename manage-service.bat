@echo off
REM POS Monitor Service Management Utility
REM Run as Administrator

:MENU
cls
echo.
echo ============================================
echo POS Monitor Service Management
echo ============================================
echo.
echo 1. Check service status
echo 2. Start service
echo 3. Stop service
echo 4. Restart service
echo 5. View service configuration
echo 6. View recent logs
echo 7. Open log directory
echo 8. Edit configuration
echo 9. Exit
echo.

choice /C 123456789 /M "Select an option"
set choice=%errorLevel%

if %choice% equ 1 goto STATUS
if %choice% equ 2 goto START
if %choice% equ 3 goto STOP
if %choice% equ 4 goto RESTART
if %choice% equ 5 goto CONFIG
if %choice% equ 6 goto LOGS
if %choice% equ 7 goto OPENDIR
if %choice% equ 8 goto EDIT
if %choice% equ 9 exit /b 0

:STATUS
echo.
echo Checking service status...
echo.
sc query POSMonitor
echo.
echo Service configuration:
sc qc POSMonitor | findstr /C:"START_TYPE" /C:"SERVICE_START_NAME"
echo.
pause
goto MENU

:START
echo.
echo Starting POS Monitor service...
net start POSMonitor
if %errorLevel% equ 0 (
    echo Service started successfully!
) else (
    echo Failed to start service. Check if it's already running or view logs.
)
pause
goto MENU

:STOP
echo.
echo Stopping POS Monitor service...
net stop POSMonitor
if %errorLevel% equ 0 (
    echo Service stopped successfully!
) else (
    echo Failed to stop service.
)
pause
goto MENU

:RESTART
echo.
echo Restarting POS Monitor service...
net stop POSMonitor >nul 2>&1
timeout /t 2 /nobreak >nul
net start POSMonitor
if %errorLevel% equ 0 (
    echo Service restarted successfully!
) else (
    echo Failed to restart service.
)
pause
goto MENU

:CONFIG
echo.
echo Service Configuration:
echo =====================
echo.
if exist "C:\ProgramData\POSMonitor\pos-monitor-config.json" (
    type "C:\ProgramData\POSMonitor\pos-monitor-config.json"
) else (
    echo Configuration file not found at C:\ProgramData\POSMonitor\pos-monitor-config.json
)
echo.
pause
goto MENU

:LOGS
echo.
echo Recent Log Entries:
echo ==================
echo.

REM Find the most recent log file
set "logdir=C:\ProgramData\POSMonitor\logs"
if not exist "%logdir%" (
    echo Log directory not found: %logdir%
    pause
    goto MENU
)

REM Get today's date in YYYY-MM-DD format
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set today=%datetime:~0,4%-%datetime:~4,2%-%datetime:~6,2%

REM Look for today's log file
set "logfile=%logdir%\pos_monitor_%today%.json"
if exist "%logfile%" (
    echo Showing last 20 entries from today's log:
    echo.
    powershell -Command "Get-Content '%logfile%' -Tail 20 | ForEach-Object { $_ | ConvertFrom-Json | ConvertTo-Json -Compress }"
) else (
    echo No log file found for today. Showing service log:
    if exist "%logdir%\service.log" (
        powershell -Command "Get-Content '%logdir%\service.log' -Tail 20"
    )
)

echo.
pause
goto MENU

:OPENDIR
echo.
echo Opening log directory...
start "" "C:\ProgramData\POSMonitor\logs"
goto MENU

:EDIT
echo.
echo Opening configuration file for editing...
if exist "C:\ProgramData\POSMonitor\pos-monitor-config.json" (
    notepad "C:\ProgramData\POSMonitor\pos-monitor-config.json"
    echo.
    echo NOTE: Restart the service for changes to take effect.
) else (
    echo Configuration file not found!
    echo Please create: C:\ProgramData\POSMonitor\pos-monitor-config.json
)
pause
goto MENU