@echo off
REM POS Monitor MSI Installer Build Script
REM Requires WiX Toolset v3.11 or higher

echo.
echo ============================================
echo POS Monitor MSI Installer Builder
echo ============================================
echo.

REM Check if WiX is installed
where candle >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: WiX Toolset is not installed or not in PATH
    echo Please download and install WiX Toolset from:
    echo https://wixtoolset.org/releases/
    pause
    exit /b 1
)

REM Check if executables exist
if not exist "dist\POSMonitor\POSMonitorService.exe" (
    echo ERROR: Executables not found. Please run build.bat first.
    pause
    exit /b 1
)

REM Change to installer directory
cd installer

REM Clean previous builds
echo [1/5] Cleaning previous builds...
if exist "*.wixobj" del /F /Q "*.wixobj"
if exist "*.wixpdb" del /F /Q "*.wixpdb"
if exist "*.msi" del /F /Q "*.msi"

REM Create assets if missing
echo [2/5] Preparing assets...
if not exist "..\assets\pos-monitor.ico" (
    echo WARNING: Icon file missing. Using default.
    echo. > "..\assets\pos-monitor.ico"
)

if not exist "License.rtf" (
    echo Creating default license file...
    echo {\rtf1\ansi\deff0 {\fonttbl{\f0 Times New Roman;}} > License.rtf
    echo \f0\fs24 POS Monitor License Agreement\par >> License.rtf
    echo \par >> License.rtf
    echo Copyright (c) 2025 UniSight. All rights reserved.\par >> License.rtf
    echo \par >> License.rtf
    echo This software is proprietary and confidential.\par >> License.rtf
    echo } >> License.rtf
)

if not exist "banner.bmp" (
    echo WARNING: Banner image missing. Installer will use default.
)

if not exist "dialog.bmp" (
    echo WARNING: Dialog image missing. Installer will use default.
)

REM Compile WiX source
echo [3/5] Compiling installer source...
candle -arch x64 POSMonitor.wxs -ext WixUtilExtension
if %errorLevel% neq 0 (
    echo ERROR: Failed to compile installer source
    cd ..
    pause
    exit /b 1
)

REM Link to create MSI
echo [4/5] Creating MSI installer...
light -ext WixUIExtension -ext WixUtilExtension POSMonitor.wixobj -o POSMonitor.msi
if %errorLevel% neq 0 (
    echo ERROR: Failed to create MSI installer
    cd ..
    pause
    exit /b 1
)

REM Move to output directory
echo [5/5] Finalizing installer...
move POSMonitor.msi ..\output\POSMonitor_v1.0.0_Setup.msi >nul

REM Clean up
del /F /Q "*.wixobj" 2>nul
del /F /Q "*.wixpdb" 2>nul

cd ..

echo.
echo ============================================
echo Installer Build Complete!
echo ============================================
echo.
echo Output: output\POSMonitor_v1.0.0_Setup.msi
echo.
echo The installer will:
echo - Install POS Monitor to Program Files
echo - Create Windows service
echo - Configure auto-start
echo - Create Start Menu shortcuts
echo - Set up logging directory
echo.
echo Test the installer on a clean Windows system.
echo.

pause