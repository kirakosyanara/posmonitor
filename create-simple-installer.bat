@echo off
REM Simple Installer Package Creator
REM Creates a self-extracting archive for easy deployment

echo.
echo ============================================
echo POS Monitor Simple Installer Creator
echo ============================================
echo.

REM Check if build exists
if not exist "dist\POSMonitor" (
    echo ERROR: Build not found. Please run build.bat first.
    pause
    exit /b 1
)

REM Create installer structure
echo [1/4] Creating installer structure...
if exist "temp_installer" rmdir /S /Q "temp_installer"
mkdir "temp_installer"
mkdir "temp_installer\POSMonitor"

REM Copy files
echo [2/4] Copying files...
xcopy /E /I /Y "dist\POSMonitor\*" "temp_installer\POSMonitor\" >nul

REM Create setup script
echo [3/4] Creating setup script...
(
echo @echo off
echo REM POS Monitor Setup
echo.
echo echo.
echo echo ============================================
echo echo POS Monitor Installation
echo echo ============================================
echo echo.
echo.
echo REM Check admin
echo net session ^>nul 2^>^&1
echo if %%errorLevel%% neq 0 ^(
echo     echo ERROR: Administrator privileges required!
echo     echo Right-click and select "Run as administrator"
echo     pause
echo     exit /b 1
echo ^)
echo.
echo REM Create directories
echo echo Installing POS Monitor...
echo set "INSTALL_DIR=%%ProgramFiles%%\UniSight\POS Monitor"
echo set "DATA_DIR=%%ProgramData%%\POSMonitor"
echo.
echo if not exist "%%INSTALL_DIR%%" mkdir "%%INSTALL_DIR%%"
echo if not exist "%%DATA_DIR%%" mkdir "%%DATA_DIR%%"
echo if not exist "%%DATA_DIR%%\logs" mkdir "%%DATA_DIR%%\logs"
echo.
echo REM Copy files
echo xcopy /E /I /Y "POSMonitor\*" "%%INSTALL_DIR%%\" ^>nul
echo.
echo REM Copy config
echo if not exist "%%DATA_DIR%%\pos-monitor-config.json" ^(
echo     copy "%%INSTALL_DIR%%\pos-monitor-config.json" "%%DATA_DIR%%\" ^>nul
echo ^)
echo.
echo REM Install service
echo echo Installing Windows service...
echo cd /d "%%INSTALL_DIR%%"
echo POSMonitorService.exe install
echo.
echo REM Create shortcuts
echo echo Creating shortcuts...
echo powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%%USERPROFILE%%\Desktop\POS Monitor Manager.lnk'); $Shortcut.TargetPath = '%%INSTALL_DIR%%\manage-service.bat'; $Shortcut.WorkingDirectory = '%%INSTALL_DIR%%'; $Shortcut.IconLocation = '%%INSTALL_DIR%%\POSMonitorService.exe'; $Shortcut.Save()"
echo.
echo echo.
echo echo ============================================
echo echo Installation Complete!
echo echo ============================================
echo echo.
echo echo POS Monitor has been installed to:
echo echo %%INSTALL_DIR%%
echo echo.
echo echo To start the service:
echo echo   net start POSMonitor
echo echo.
echo echo To manage the service:
echo echo   Use the desktop shortcut or run manage-service.bat
echo echo.
echo pause
) > "temp_installer\setup.bat"

REM Create self-extracting archive
echo [4/4] Creating self-extracting installer...
cd temp_installer

REM Create SFX configuration
(
echo ;!@Install@!UTF-8!
echo Title="POS Monitor Setup"
echo BeginPrompt="This will install POS Monitor on your computer.\n\nPress OK to continue or Cancel to exit."
echo RunProgram="setup.bat"
echo ;!@InstallEnd@!
) > config.txt

REM Use 7-Zip if available, otherwise use PowerShell
where 7z >nul 2>&1
if %errorLevel% equ 0 (
    7z a -sfx7z.sfx ..\output\POSMonitor_v1.0.0_Setup.exe * -mx=9
) else (
    REM Fallback to PowerShell compression
    powershell -Command "Compress-Archive -Path '*' -DestinationPath '..\output\POSMonitor_v1.0.0_Setup.zip' -Force"
    echo.
    echo NOTE: 7-Zip not found. Created ZIP file instead of self-extracting EXE.
    echo To create EXE installer, install 7-Zip and run this script again.
)

cd ..

REM Clean up
rmdir /S /Q "temp_installer"

echo.
echo ============================================
echo Simple Installer Created!
echo ============================================
echo.
if exist "output\POSMonitor_v1.0.0_Setup.exe" (
    echo Output: output\POSMonitor_v1.0.0_Setup.exe
) else (
    echo Output: output\POSMonitor_v1.0.0_Setup.zip
    echo Extract and run setup.bat as Administrator
)
echo.

pause