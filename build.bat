@echo off
REM POS Monitor Build Script
REM Builds the application using PyInstaller

echo.
echo ============================================
echo POS Monitor Build System
echo ============================================
echo.

REM Check Python
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Clean previous builds
echo [1/6] Cleaning previous builds...
if exist "build" rmdir /S /Q "build"
if exist "dist" rmdir /S /Q "dist"
if exist "__pycache__" rmdir /S /Q "__pycache__"
if exist "*.pyc" del /F /Q "*.pyc"

REM Create directories
echo [2/6] Creating directories...
if not exist "assets" mkdir "assets"
if not exist "output" mkdir "output"

REM Install/Update dependencies
echo [3/6] Installing dependencies...
pip install --upgrade pip >nul
pip install pyinstaller==6.3.0 --no-warn-script-location
pip install -r pos-monitor-requirements.txt --no-warn-script-location

REM Create icon if missing (placeholder)
if not exist "assets\pos-monitor.ico" (
    echo Creating placeholder icon...
    echo. > "assets\pos-monitor.ico"
)

REM Build executables
echo [4/6] Building executables with PyInstaller...
pyinstaller --clean --noconfirm pos-monitor.spec

if %errorLevel% neq 0 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

REM Copy configuration and scripts
echo [5/6] Copying support files...
copy "pos-monitor-config.json" "dist\POSMonitor\" >nul
copy "install-service.bat" "dist\POSMonitor\" >nul
copy "uninstall-service.bat" "dist\POSMonitor\" >nul
copy "manage-service.bat" "dist\POSMonitor\" >nul
copy "POSMonitor-ServiceManager.ps1" "dist\POSMonitor\" >nul
copy "SERVICE-TROUBLESHOOTING.md" "dist\POSMonitor\" >nul
copy "README.md" "dist\POSMonitor\" >nul

REM Create deployment package
echo [6/6] Creating deployment package...
set VERSION=1.0.0
set TIMESTAMP=%date:~-4%%date:~4,2%%date:~7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set TIMESTAMP=%TIMESTAMP: =0%
set PACKAGE_NAME=POSMonitor_v%VERSION%_%TIMESTAMP%

cd dist
powershell -Command "Compress-Archive -Path 'POSMonitor\*' -DestinationPath '..\output\%PACKAGE_NAME%.zip' -Force"
cd ..

echo.
echo ============================================
echo Build Complete!
echo ============================================
echo.
echo Output files:
echo - Executable: dist\POSMonitor\POSMonitorService.exe
echo - Package: output\%PACKAGE_NAME%.zip
echo.
echo Next steps:
echo 1. Test the executable on a clean system
echo 2. Build MSI installer using create-installer.bat
echo.

pause