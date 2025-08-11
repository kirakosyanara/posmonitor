# POS Monitor

A Windows service application that monitors JavaFX Point of Sale (POS) applications for performance metrics, hangs, and crashes without requiring any modifications to the target application.

## Current Development Status: Phase 2 Complete ✅

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

### 🚧 Next Phase: Packaging & Deployment (Phase 3)

- PyInstaller executable packaging
- MSI installer with WiX toolset
- Embedded Python distribution
- Production deployment package

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

## Project Status

- **Phase 1**: Core Features ✅ Complete
- **Phase 2**: Windows Service ✅ Complete  
- **Phase 3**: Packaging & Deployment 🚧 Next
- **Phase 4**: Documentation & Polish 📋 Planned

See [development-plan.md](development-plan.md) for detailed roadmap.

## License

This project is proprietary software for UniSight POS monitoring.
