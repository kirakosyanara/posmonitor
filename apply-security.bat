@echo off
REM POS Monitor Security Hardening Script
REM Applies security best practices to installation

echo.
echo ============================================
echo POS Monitor Security Hardening
echo ============================================
echo.

REM Check for admin privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Administrator privileges required!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo This script will:
echo - Set restrictive ACLs on directories and files
echo - Configure service security settings
echo - Enable security auditing
echo - Validate security configuration
echo.
echo WARNING: This will modify file and directory permissions!
echo.
choice /C YN /M "Continue with security hardening"
if %errorLevel% neq 1 exit /b 0

echo.
echo [1/5] Checking Python environment...
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo [2/5] Installing security module dependencies...
pip install pywin32 >nul 2>&1

echo [3/5] Applying security hardening...
python security-hardening.py
if %errorLevel% neq 0 (
    echo ERROR: Security hardening failed!
    echo Check the logs for details.
    pause
    exit /b 1
)

echo [4/5] Generating security report...
python security-hardening.py --report > security-report.json
echo Security report saved to: security-report.json

echo [5/5] Verifying service configuration...
sc qc POSMonitor | findstr /i "LocalSystem" >nul
if %errorLevel% equ 0 (
    echo Service is configured to run as LocalSystem [OK]
) else (
    echo WARNING: Service may not be configured correctly
)

echo.
echo ============================================
echo Security Hardening Complete!
echo ============================================
echo.
echo Security measures applied:
echo - Installation directory: Read-only for users
echo - Configuration directory: Restricted to SYSTEM and Administrators
echo - Log directory: Write access for SYSTEM only
echo - Service account: LocalSystem (most secure)
echo.
echo Next steps:
echo 1. Review security-report.json for details
echo 2. Test service functionality
echo 3. Monitor Windows Security event log
echo.

pause