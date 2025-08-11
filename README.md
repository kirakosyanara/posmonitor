# POS Monitor

A Windows service application that monitors JavaFX Point of Sale (POS) applications for performance metrics, hangs, and crashes without requiring any modifications to the target application.

## 🎉 Production Ready - Version 1.0.0

POS Monitor is now production-ready with all planned features implemented, tested, and documented. The application provides enterprise-grade monitoring for JavaFX POS applications on Windows systems.

### ✅ Complete Feature Set

#### Core Monitoring Capabilities
- **Performance Monitoring**: Real-time CPU, memory, thread, and handle tracking
- **Hang Detection**: UI responsiveness monitoring using Windows APIs
- **Event Log Integration**: Windows event monitoring with Java-specific filtering
- **Crash Detection**: Comprehensive crash analysis with exit code interpretation
- **Async Logging**: High-performance JSON logging with rotation and compression
- **Self-Monitoring**: Built-in resource limits and health checks

#### Enterprise Features
- **Windows Service**: Runs as a system service with automatic startup
- **Professional Installer**: MSI package for enterprise deployment
- **Security Hardening**: ACL-based access control and secure configuration
- **Management Tools**: PowerShell cmdlets and interactive management
- **Comprehensive Documentation**: Installation, configuration, and optimization guides
- **Production Testing**: Validated deployment and troubleshooting procedures

### 📦 Available Packages

1. **MSI Installer** (`POSMonitor_v1.0.0_Setup.msi`)
   - Professional installation experience
   - Automatic service registration
   - Start menu integration
   - Clean uninstall support

2. **Simple Installer** (`POSMonitor_v1.0.0_Setup.exe`)
   - Self-extracting archive
   - No prerequisites required
   - Quick deployment option

3. **Manual Package** (`POSMonitor_v1.0.0_[timestamp].zip`)
   - For custom deployments
   - Includes all binaries and scripts
   - Full control over installation

## Purpose

This application is designed to monitor POS systems running on Windows 10 IoT devices in retail environments. It provides real-time visibility into application health without requiring any modifications to the monitored application.

## Key Benefits

- **Zero modification required** - Works with any Windows application
- **JavaFX optimized** - Special handling for JavaFX applications
- **Lightweight** - Minimal resource usage (<50MB memory, <2% CPU)
- **Production ready** - Designed for 24/7 operation
- **Enterprise grade** - Professional installer, security hardening, comprehensive docs
- **Self-monitoring** - Built-in health checks and resource limits

## Installation and Usage

### System Requirements

- **OS**: Windows 10 (1607+) or Windows Server 2016+
- **Architecture**: x64
- **Memory**: 512 MB available RAM
- **Storage**: 100 MB + log storage
- **.NET**: Framework 4.7.2+ (included in Windows 10 1803+)
- **Privileges**: Administrator for installation

### Quick Start

1. **Download and Install**
   ```batch
   # Download POSMonitor_v1.0.0_Setup.msi
   # Run as Administrator
   msiexec /i POSMonitor_v1.0.0_Setup.msi
   ```

2. **Configure Target Process**
   Edit `C:\ProgramData\POSMonitor\pos-monitor-config.json`:
   ```json
   {
     "monitor": {
       "process_name": "YourPOSApp.exe"
     }
   }
   ```

3. **Start Monitoring**
   ```batch
   net start POSMonitor
   ```

### Service Management

**Using Batch Menu:**
```batch
manage-service.bat
```

**Using PowerShell:**
```powershell
Import-Module .\POSMonitor-ServiceManager.ps1
Get-POSMonitorStatus
Get-POSMonitorLogs -Count 20
Test-POSMonitorHealth
```

**Using Commands:**
```batch
# Start/Stop service
net start POSMonitor
net stop POSMonitor

# Check status
sc query POSMonitor
```

### Configuration

Edit `C:\ProgramData\POSMonitor\pos-monitor-config.json`:
```json
{
  "monitor": {
    "process_name": "YourPOSApp.exe",
    "performance_interval": 60,
    "hang_timeout_seconds": 5
  }
}
```

### Testing & Validation

```batch
# Validate deployment
test-deployment.bat

# Check service health
powershell -Command "Import-Module '.\POSMonitor-ServiceManager.ps1'; Test-POSMonitorHealth"

# Apply security hardening
apply-security.bat
```

## Architecture

The monitor uses a multi-threaded architecture with separate threads for:
- Performance metrics collection
- Process existence monitoring  
- UI hang detection
- Windows Event Log monitoring
- Self resource monitoring
- Async log writing

### Key Components

1. **Core Monitor** (`pos-monitor-core.py`) - Main orchestrator
2. **Hang Detector** (`pos-monitor-hang-detector.py`) - UI responsiveness
3. **Event Log Monitor** (`pos-monitor-event-log.py`) - Windows event logs
4. **Async Logger** (`pos-monitor-async-logger.py`) - High-performance logging

## Log Output

Logs are written to `C:\ProgramData\POSMonitor\logs\` in daily JSON files:
- Performance metrics every 60 seconds
- Hang events when detected
- Event log errors and warnings
- Crash details with exit codes
- Monitor health metrics every 5 minutes

Log files are automatically:
- Rotated when they exceed size limits
- Compressed when rotated
- Deleted after retention period

## Documentation

### User Guides
- [Installation Guide](docs/INSTALLATION-GUIDE.md) - Detailed installation instructions
- [Configuration Reference](docs/CONFIGURATION-REFERENCE.md) - All configuration options
- [Performance Optimization](docs/PERFORMANCE-OPTIMIZATION.md) - Tuning for your environment
- [Troubleshooting Guide](SERVICE-TROUBLESHOOTING.md) - Common issues and solutions

### Deployment Resources
- [Release Notes](RELEASE-NOTES.md) - Version history and changes
- [Deployment Checklist](DEPLOYMENT-CHECKLIST.md) - Production deployment guide
- [Development Plan](development-plan.md) - Project roadmap and status

## Building and Deployment

### Building from Source

1. **Prerequisites**
   - Python 3.8+ with pip
   - PyInstaller 6.3.0
   - Windows 10 SDK (for signing)
   - WiX Toolset 3.11+ (for MSI)

2. **Build Steps**
   ```batch
   # Install dependencies
   pip install -r pos-monitor-requirements.txt
   
   # Build executables
   build.bat
   
   # Create MSI installer (requires WiX)
   create-installer.bat
   
   # Or create simple installer
   create-simple-installer.bat
   ```

3. **Output Files**
   - `dist/POSMonitor/` - Executable files
   - `output/POSMonitor_v1.0.0_Setup.msi` - MSI installer
   - `output/POSMonitor_v1.0.0_[timestamp].zip` - Distribution package

### Deployment Options

1. **MSI Installer** (Recommended for enterprise)
   - Professional installation experience
   - Automatic service registration
   - Start menu shortcuts
   - Clean uninstall

2. **Simple Installer** (For quick deployment)
   - Self-extracting archive
   - No prerequisites required
   - Manual service installation

3. **Manual Installation**
   - Extract ZIP to Program Files
   - Run `install-service.bat` as admin
   - Configure using `manage-service.bat`

### Version Management

Update version in `version.py`:
```python
python version.py --update
```

## Project Status

**Version 1.0.0 - Production Ready** 🎉

All development phases completed:
- ✅ **Phase 1**: Core monitoring features
- ✅ **Phase 2**: Windows service implementation
- ✅ **Phase 3**: Packaging and deployment
- ✅ **Phase 4**: Documentation and security

The application is ready for production deployment with:
- Complete feature implementation
- Professional installation packages
- Comprehensive documentation
- Security hardening applied
- Performance optimization guides
- Full deployment support

See [development-plan.md](development-plan.md) for implementation details.

## Support

For assistance with POS Monitor:

1. **Documentation**: Start with the comprehensive guides in the docs folder
2. **Troubleshooting**: Check the troubleshooting guide for common issues
3. **Configuration**: Review the configuration reference for all options
4. **Performance**: See the optimization guide for tuning recommendations

## Future Enhancements

Planned features for future releases:
- Web-based monitoring dashboard
- Email and SMS alerting
- Remote configuration API
- Multi-process monitoring
- Integration with monitoring platforms
- Advanced analytics and reporting

## License

Copyright (c) 2025 UniSight. All rights reserved.

This is proprietary software designed for monitoring POS applications in retail environments.
