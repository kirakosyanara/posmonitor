# POS Monitor

A Windows service application that monitors JavaFX Point of Sale (POS) applications for performance metrics, hangs, and crashes without requiring any modifications to the target application.

## Current Development Status: Phase 3 Complete ✅

### Implemented Features

#### Phase 1: Core Monitoring & Robustness (Weeks 1-2)
- **Performance Monitoring**: CPU, memory, thread tracking with configurable intervals
- **Hang Detection**: UI responsiveness checking with JavaFX window discovery
- **Event Log Integration**: Windows event monitoring with Java error filtering
- **Crash Detection**: Exit code interpretation and crash context collection
- **Async Logging**: High-performance logging with rotation and compression
- **Self-Monitoring**: Resource usage tracking with configurable limits
- **Testing Suite**: Comprehensive unit and integration tests

#### Phase 2: Windows Service Implementation (Week 3)
- **Service Wrapper**: Full Windows service with automatic startup
- **Recovery Configuration**: Automatic restart on failure (3 attempts)
- **Installation Scripts**: One-click install/uninstall with admin checks
- **Management Tools**: Interactive batch menu and PowerShell cmdlets
- **Service Logging**: Dedicated service logs with Windows Event Log integration
- **Health Monitoring**: Built-in diagnostics and troubleshooting
- **Configuration Management**: Service-aware config file handling

#### Phase 3: Packaging & Deployment (Week 4)
- **PyInstaller Build**: Standalone executables with embedded Python
- **Version Management**: Centralized version control with auto-update
- **Build Automation**: One-click build with dependency bundling
- **MSI Installer**: Professional WiX-based installer with UI
- **Simple Installer**: Self-extracting archive alternative
- **Deployment Testing**: Comprehensive validation and verification
- **Package Output**: Ready-to-distribute ZIP and MSI packages

### 🚧 Next Phase: Documentation & Polish (Phase 4)

- Complete user documentation
- Security hardening and ACLs
- Performance optimization
- Final production testing

### 📋 Future Enhancements

- Advanced security features (ACLs, encryption)
- Web dashboard for real-time monitoring
- Remote monitoring API
- Multi-process monitoring support

## Purpose

This application is designed to monitor POS systems running on Windows 10 IoT devices in retail environments. It provides real-time visibility into application health without requiring any modifications to the monitored application.

## Key Benefits

- **Zero modification required** - Works with any Windows application
- **JavaFX optimized** - Special handling for JavaFX applications
- **Lightweight** - Minimal resource usage (<50MB memory)
- **Production ready** - Designed for 24/7 operation

## Installation and Usage

### Prerequisites

- Windows 10 or later
- Python 3.8+ 
- Administrator privileges
- Required packages: `pip install -r pos-monitor-requirements.txt`

### Service Installation

1. **Quick Install** (Recommended)
   ```batch
   # Run as Administrator
   install-service.bat
   ```

2. **Manual Install**
   ```batch
   python pos-monitor-service.py install
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

### Testing

```bash
# Test core functionality
python pos-monitor-test.py

# Test service installation
test-service.bat

# Run unit tests
python run_tests.py
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

## Troubleshooting

See [SERVICE-TROUBLESHOOTING.md](SERVICE-TROUBLESHOOTING.md) for common issues and solutions.

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

- **Phase 1**: Core Features ✅ Complete
- **Phase 2**: Windows Service ✅ Complete  
- **Phase 3**: Packaging & Deployment ✅ Complete
- **Phase 4**: Documentation & Polish 🚧 Next

See [development-plan.md](development-plan.md) for detailed roadmap.

## License

This project is proprietary software for UniSight POS monitoring.
