@echo off
REM POS Monitor Service Test Script
REM Tests service installation, lifecycle, and recovery

echo.
echo ============================================
echo POS Monitor Service Test Suite
echo ============================================
echo.

REM Check for administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    pause
    exit /b 1
)

cd /d %~dp0

echo [TEST 1] Service Installation Test
echo ==================================
echo Installing service...
call install-service.bat < nul
if %errorLevel% neq 0 (
    echo FAILED: Service installation failed
    pause
    exit /b 1
)
echo PASSED: Service installed successfully
echo.

timeout /t 3 /nobreak >nul

echo [TEST 2] Service Start Test
echo ===========================
echo Starting service...
net start POSMonitor
if %errorLevel% equ 0 (
    echo PASSED: Service started successfully
) else (
    echo FAILED: Service failed to start
    sc query POSMonitor
    pause
    exit /b 1
)
echo.

timeout /t 5 /nobreak >nul

echo [TEST 3] Service Status Test
echo ============================
sc query POSMonitor | findstr "RUNNING"
if %errorLevel% equ 0 (
    echo PASSED: Service is running
) else (
    echo FAILED: Service is not in running state
)
echo.

echo [TEST 4] Log Creation Test
echo ==========================
if exist "C:\ProgramData\POSMonitor\logs\service.log" (
    echo PASSED: Service log file created
    echo Last 5 lines of service log:
    powershell -Command "Get-Content 'C:\ProgramData\POSMonitor\logs\service.log' -Tail 5"
) else (
    echo FAILED: Service log file not found
)
echo.

echo [TEST 5] Service Stop Test
echo ==========================
echo Stopping service...
net stop POSMonitor
if %errorLevel% equ 0 (
    echo PASSED: Service stopped successfully
) else (
    echo FAILED: Service failed to stop
)
echo.

timeout /t 3 /nobreak >nul

echo [TEST 6] Auto-Start Configuration Test
echo ======================================
sc qc POSMonitor | findstr "AUTO_START"
if %errorLevel% equ 0 (
    echo PASSED: Service configured for auto-start
) else (
    echo FAILED: Service not configured for auto-start
)
echo.

echo [TEST 7] Recovery Configuration Test
echo ====================================
sc qfailure POSMonitor | findstr "restart"
if %errorLevel% equ 0 (
    echo PASSED: Service recovery actions configured
) else (
    echo FAILED: Service recovery not configured
)
echo.

echo [TEST 8] Service Restart Test
echo =============================
echo Starting service again...
net start POSMonitor >nul 2>&1
timeout /t 3 /nobreak >nul

echo Simulating crash by killing process...
for /f "tokens=2" %%i in ('sc queryex POSMonitor ^| findstr "PID"') do set PID=%%i
taskkill /PID %PID% /F >nul 2>&1

echo Waiting for automatic recovery (60 seconds)...
timeout /t 65 /nobreak

sc query POSMonitor | findstr "RUNNING"
if %errorLevel% equ 0 (
    echo PASSED: Service automatically recovered
) else (
    echo FAILED: Service did not recover automatically
)
echo.

echo [TEST 9] Uninstallation Test
echo ============================
echo Uninstalling service...
net stop POSMonitor >nul 2>&1
python pos-monitor-service.py remove
if %errorLevel% equ 0 (
    echo PASSED: Service uninstalled successfully
) else (
    echo FAILED: Service uninstallation failed
)
echo.

echo ============================================
echo Test Suite Complete
echo ============================================
echo.
echo Review the results above for any failures.
echo If all tests passed, the service is ready for production use.
echo.

pause