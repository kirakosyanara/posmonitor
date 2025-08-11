# POS Monitor Installation Guide

## Table of Contents
- [System Requirements](#system-requirements)
- [Pre-Installation Checklist](#pre-installation-checklist)
- [Installation Methods](#installation-methods)
  - [Method 1: MSI Installer (Recommended)](#method-1-msi-installer-recommended)
  - [Method 2: Simple Installer](#method-2-simple-installer)
  - [Method 3: Manual Installation](#method-3-manual-installation)
- [Post-Installation Configuration](#post-installation-configuration)
- [Verifying Installation](#verifying-installation)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

## System Requirements

### Minimum Requirements
- **Operating System**: Windows 10 (version 1607 or later), Windows Server 2016+
- **Memory**: 512 MB RAM available
- **Storage**: 100 MB free disk space
- **Processor**: x64 architecture
- **Privileges**: Administrator rights for installation

### Supported Editions
- Windows 10 Pro/Enterprise/IoT Enterprise
- Windows 11 Pro/Enterprise
- Windows Server 2016/2019/2022

### Prerequisites
- .NET Framework 4.7.2 or later (included in Windows 10 1803+)
- Visual C++ Redistributable 2015-2022 (included in installer)

## Pre-Installation Checklist

Before installing POS Monitor, ensure:

1. ✅ **Administrator Access**: You have administrative privileges
2. ✅ **Target Application**: The POS application to monitor is installed
3. ✅ **Antivirus**: Whitelist the installation directory if needed
4. ✅ **Backup**: Current monitoring configuration is backed up (if upgrading)
5. ✅ **Network**: No proxy blocking local Windows service communication

## Installation Methods

### Method 1: MSI Installer (Recommended)

**Best for**: Enterprise deployments, Group Policy installation, automated deployment

1. **Download the Installer**
   - Download `POSMonitor_v1.0.0_Setup.msi` from your distribution source
   - Verify the file integrity using provided checksums

2. **Run the Installer**
   ```cmd
   # Right-click the MSI file and select "Install"
   # OR run from command line:
   msiexec /i POSMonitor_v1.0.0_Setup.msi
   ```

3. **Follow Installation Wizard**
   - Click "Next" on the welcome screen
   - Accept the license agreement
   - Choose installation directory (default: `C:\Program Files\UniSight\POS Monitor`)
   - Select features (all recommended)
   - Click "Install"
   - Wait for installation to complete

4. **Installation Options**
   - **Silent Install**: `msiexec /i POSMonitor_v1.0.0_Setup.msi /quiet`
   - **With Logging**: `msiexec /i POSMonitor_v1.0.0_Setup.msi /l*v install.log`
   - **Custom Directory**: `msiexec /i POSMonitor_v1.0.0_Setup.msi INSTALLDIR="D:\POSMonitor"`

### Method 2: Simple Installer

**Best for**: Quick deployment, testing environments

1. **Download and Extract**
   - Download `POSMonitor_v1.0.0_Setup.exe` (self-extracting archive)
   - Run as Administrator

2. **Execute Setup**
   - The installer will extract files to a temporary directory
   - Follow the on-screen prompts
   - Service will be installed automatically

### Method 3: Manual Installation

**Best for**: Custom deployments, scripted installations

1. **Extract Files**
   ```cmd
   # Create installation directory
   mkdir "C:\Program Files\UniSight\POS Monitor"
   
   # Extract ZIP package to installation directory
   # Copy all files from the distribution package
   ```

2. **Create Data Directory**
   ```cmd
   mkdir "C:\ProgramData\POSMonitor"
   mkdir "C:\ProgramData\POSMonitor\logs"
   ```

3. **Copy Configuration**
   ```cmd
   copy "C:\Program Files\UniSight\POS Monitor\pos-monitor-config.json" ^
        "C:\ProgramData\POSMonitor\"
   ```

4. **Install Service**
   ```cmd
   cd "C:\Program Files\UniSight\POS Monitor"
   POSMonitorService.exe install
   ```

5. **Configure Service**
   ```cmd
   # Set to auto-start
   sc config POSMonitor start=auto
   
   # Configure recovery options
   sc failure POSMonitor reset=86400 actions=restart/60000/restart/60000/restart/60000
   ```

## Post-Installation Configuration

### 1. Configure Monitoring Target

Edit `C:\ProgramData\POSMonitor\pos-monitor-config.json`:

```json
{
  "monitor": {
    "process_name": "YourPOSApplication.exe",
    "performance_interval": 60,
    "hang_detection": {
      "enabled": true,
      "timeout_seconds": 5,
      "check_interval": 30
    }
  }
}
```

### 2. Start the Service

```cmd
# Start immediately
net start POSMonitor

# Or use Service Manager
services.msc
# Find "POS Application Monitor" and start it
```

### 3. Configure Firewall (if needed)

```powershell
# Allow service communication
New-NetFirewallRule -DisplayName "POS Monitor Service" `
  -Direction Inbound -Program "%ProgramFiles%\UniSight\POS Monitor\POSMonitorService.exe" `
  -Action Allow -Protocol TCP
```

## Verifying Installation

### 1. Check Service Status
```cmd
sc query POSMonitor
# Should show: STATE: 4 RUNNING
```

### 2. Verify Log Creation
```cmd
dir "C:\ProgramData\POSMonitor\logs"
# Should see pos_monitor_YYYY-MM-DD.json files
```

### 3. Test Monitoring
```powershell
# Use the management tools
Import-Module "C:\Program Files\UniSight\POS Monitor\POSMonitor-ServiceManager.ps1"
Test-POSMonitorHealth
```

### 4. Check Event Log
```cmd
eventvwr.msc
# Navigate to: Applications and Services Logs > POSMonitor
```

## Troubleshooting

### Service Won't Start

1. **Check Prerequisites**
   ```cmd
   # Verify .NET Framework
   reg query "HKLM\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full" /v Release
   # Should be 461808 or higher
   ```

2. **Check Permissions**
   ```cmd
   # Ensure service account has access
   icacls "C:\ProgramData\POSMonitor" /grant "NT AUTHORITY\SYSTEM:(OI)(CI)F"
   ```

3. **Review Event Log**
   ```cmd
   eventvwr.msc
   # Check Windows Logs > Application for errors
   ```

### Installation Failed

1. **MSI Install Issues**
   ```cmd
   # Run with logging
   msiexec /i POSMonitor_v1.0.0_Setup.msi /l*v install_debug.log
   # Review install_debug.log for errors
   ```

2. **Permission Denied**
   - Ensure running as Administrator
   - Disable UAC temporarily if needed
   - Check antivirus logs

### Monitor Not Detecting Application

1. **Verify Process Name**
   ```cmd
   # List running processes
   tasklist | findstr /i "yourapp"
   # Use exact name in config
   ```

2. **Check Configuration**
   ```cmd
   # Validate JSON syntax
   type "C:\ProgramData\POSMonitor\pos-monitor-config.json"
   ```

## Uninstallation

### Using MSI Installer
```cmd
# Via Control Panel
# Programs and Features > POS Monitor > Uninstall

# Via Command Line
msiexec /x POSMonitor_v1.0.0_Setup.msi /quiet

# Or using product code
msiexec /x {YOUR-PRODUCT-GUID} /quiet
```

### Manual Uninstallation
```cmd
# Stop and remove service
net stop POSMonitor
sc delete POSMonitor

# Remove files
rmdir /S /Q "C:\Program Files\UniSight\POS Monitor"
rmdir /S /Q "C:\ProgramData\POSMonitor"

# Remove shortcuts
del "%USERPROFILE%\Desktop\POS Monitor Manager.lnk"
del "%ProgramData%\Microsoft\Windows\Start Menu\Programs\POS Monitor\*"
```

## Next Steps

After successful installation:

1. Review [Configuration Reference](CONFIGURATION-REFERENCE.md) for advanced settings
2. Set up monitoring alerts and notifications
3. Configure log retention policies
4. Test monitoring with your specific POS application
5. Document any custom configurations

## Support

For installation support:
- Check [Troubleshooting Guide](../SERVICE-TROUBLESHOOTING.md)
- Review Windows Event Logs
- Contact your system administrator
- Submit issues to the support team