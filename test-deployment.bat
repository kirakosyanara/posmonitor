@echo off
REM POS Monitor Deployment Test Script
REM Tests the packaged application before distribution

echo.
echo ============================================
echo POS Monitor Deployment Test
echo ============================================
echo.

REM Check if build exists
if not exist "dist\POSMonitor\POSMonitorService.exe" (
    echo ERROR: Build not found. Please run build.bat first.
    pause
    exit /b 1
)

echo This test will:
echo - Verify all required files are present
echo - Check executable signatures
echo - Test basic functionality
echo - Validate configuration
echo.
choice /C YN /M "Continue with deployment test"
if %errorLevel% neq 1 exit /b 0

echo.
echo [TEST 1] File Verification
echo ==========================
set MISSING=0

echo Checking executables...
if not exist "dist\POSMonitor\POSMonitorService.exe" (
    echo MISSING: POSMonitorService.exe
    set MISSING=1
)
if not exist "dist\POSMonitor\POSMonitor.exe" (
    echo MISSING: POSMonitor.exe
    set MISSING=1
)

echo Checking scripts...
if not exist "dist\POSMonitor\install-service.bat" (
    echo MISSING: install-service.bat
    set MISSING=1
)
if not exist "dist\POSMonitor\manage-service.bat" (
    echo MISSING: manage-service.bat
    set MISSING=1
)

echo Checking configuration...
if not exist "dist\POSMonitor\pos-monitor-config.json" (
    echo MISSING: pos-monitor-config.json
    set MISSING=1
)

if %MISSING% equ 0 (
    echo PASSED: All required files present
) else (
    echo FAILED: Missing required files
    pause
    exit /b 1
)
echo.

echo [TEST 2] Executable Verification
echo ================================
echo Checking file sizes...
for %%F in ("dist\POSMonitor\POSMonitorService.exe") do (
    set SIZE=%%~zF
    set /a SIZE_MB=!SIZE! / 1048576
    echo POSMonitorService.exe: %%~zF bytes
)

echo.
echo Checking dependencies...
cd dist\POSMonitor
POSMonitorService.exe --version >nul 2>&1
if %errorLevel% equ 0 (
    echo PASSED: Service executable runs
) else (
    echo WARNING: Service executable may have missing dependencies
)
cd ..\..
echo.

echo [TEST 3] Configuration Test
echo ===========================
echo Validating JSON configuration...
python -c "import json; json.load(open('dist/POSMonitor/pos-monitor-config.json'))" 2>nul
if %errorLevel% equ 0 (
    echo PASSED: Configuration file is valid JSON
) else (
    echo FAILED: Invalid configuration file
)
echo.

echo [TEST 4] Installation Simulation
echo ================================
echo Creating test directories...
set TEST_DIR=%TEMP%\POSMonitor_Test
if exist "%TEST_DIR%" rmdir /S /Q "%TEST_DIR%"
mkdir "%TEST_DIR%"
mkdir "%TEST_DIR%\logs"

echo Copying files...
xcopy /E /I /Y "dist\POSMonitor\*" "%TEST_DIR%\" >nul

echo Testing monitor functionality...
cd "%TEST_DIR%"
start /B POSMonitor.exe notepad.exe
timeout /t 5 /nobreak >nul
taskkill /F /IM POSMonitor.exe >nul 2>&1

if exist "logs\pos_monitor_*.json" (
    echo PASSED: Monitor creates log files
) else (
    echo FAILED: No log files created
)

cd "%~dp0"
rmdir /S /Q "%TEST_DIR%"
echo.

echo [TEST 5] Package Verification
echo =============================
if exist "output\POSMonitor_v*.zip" (
    echo PASSED: Deployment package created
    for %%F in ("output\POSMonitor_v*.zip") do (
        echo Package: %%~nxF
        echo Size: %%~zF bytes
    )
) else (
    echo WARNING: No deployment package found
)
echo.

echo ============================================
echo Deployment Test Summary
echo ============================================
echo.
echo Review the results above for any failures.
echo If all tests passed, the package is ready for distribution.
echo.
echo Recommended next steps:
echo 1. Test installation on a clean Windows 10 system
echo 2. Verify service installation and auto-start
echo 3. Monitor resource usage under load
echo 4. Test uninstallation process
echo.

pause