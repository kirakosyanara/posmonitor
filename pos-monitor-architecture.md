# POS Application Monitor - Architecture Document

## System Overview
A Windows service that monitors a JavaFX POS application for performance metrics, hangs, and crashes without requiring any modifications to the target application.

## Core Components

### 1. Process Monitor
- **Purpose**: Track CPU/memory usage and process health
- **Technology**: `psutil` library
- **Sampling Rate**: Every 60 seconds
- **Metrics Collected**:
  - CPU percentage
  - Memory usage (RSS, VMS, percent)
  - Thread count
  - Handle count
  - Process status

### 2. Hang Detector
- **Purpose**: Detect UI unresponsiveness
- **Method**: SendMessageTimeout to main window
- **Threshold**: 5 seconds timeout
- **Technology**: `pywin32` Windows API

### 3. Event Log Monitor
- **Purpose**: Capture application errors and crashes
- **Sources**: 
  - Windows Application Event Log
  - System Event Log
- **Filters**: 
  - Process name matching
  - Java/JVM specific errors
  - Error/Warning/Critical levels

### 4. Crash Monitor
- **Purpose**: Detect unexpected process termination
- **Method**: Process existence polling + exit code monitoring
- **Additional**: Capture crash dumps if available

### 5. Data Logger
- **Format**: JSON with timestamp
- **Structure**: Time-series for metrics, event-based for errors
- **Location**: `C:\ProgramData\POSMonitor\logs\`
- **Rotation**: Daily files with date stamps

## Service Architecture

### Windows Service Structure
```
POSMonitor Service
├── Main Service Thread
│   ├── Process Discovery
│   └── Monitoring Loop Coordinator
├── Performance Monitor Thread
│   └── 60-second sampling
├── Hang Detector Thread
│   └── 5-second UI check interval
├── Event Log Monitor Thread
│   └── Real-time event subscription
└── Logger Thread
    └── Async write queue
```

## Data Schema

### Performance Metrics (every 60 seconds)
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "type": "performance",
  "process_name": "YourPOSApp.exe",
  "pid": 1234,
  "metrics": {
    "cpu_percent": 15.2,
    "memory_rss_mb": 256.5,
    "memory_vms_mb": 512.3,
    "memory_percent": 3.2,
    "thread_count": 45,
    "handle_count": 523
  }
}
```

### Hang Event
```json
{
  "timestamp": "2024-01-15T10:31:15Z",
  "type": "hang",
  "process_name": "YourPOSApp.exe",
  "pid": 1234,
  "duration_seconds": 5.2,
  "window_title": "POS System - Store #123",
  "recovered": true
}
```

### Error Event
```json
{
  "timestamp": "2024-01-15T10:32:00Z",
  "type": "error",
  "process_name": "YourPOSApp.exe",
  "pid": 1234,
  "source": "Application",
  "event_id": 1000,
  "level": "Error",
  "message": "java.lang.OutOfMemoryError: Java heap space",
  "details": {
    "stack_trace": "..."
  }
}
```

### Crash Event
```json
{
  "timestamp": "2024-01-15T10:33:00Z",
  "type": "crash",
  "process_name": "YourPOSApp.exe",
  "pid": 1234,
  "exit_code": -1073741819,
  "uptime_seconds": 3600,
  "last_known_state": {
    "cpu_percent": 95.2,
    "memory_rss_mb": 1024.5
  }
}
```

## Security Considerations

1. **Service Permissions**
   - Run as Local System or dedicated service account
   - Read-only access to target process
   - Write access only to log directory

2. **Log Security**
   - Restricted ACL on log directory
   - No sensitive POS data collection
   - Performance metrics only

3. **Resource Limits**
   - Maximum 50MB memory usage
   - CPU usage throttling
   - Log file size monitoring

## Deployment Strategy

1. **Installation**
   - Python 3.8+ embedded distribution
   - All dependencies included
   - Single MSI installer

2. **Configuration**
   - `config.json` for process name and thresholds
   - No registry modifications
   - Easy uninstall

## Development Phases

### Phase 1: Core Monitoring (Week 1)
- Process discovery and tracking
- Basic CPU/memory logging
- JSON file output

### Phase 2: Hang Detection (Week 2)
- Window message monitoring
- Timeout detection
- Recovery tracking

### Phase 3: Event Log Integration (Week 3)
- Windows Event Log subscription
- Java error parsing
- Crash detection

### Phase 4: Service Wrapper (Week 4)
- Windows service implementation
- Auto-start configuration
- Installer creation

## Testing Strategy

1. **Unit Tests**
   - Mock process monitoring
   - Event log parsing
   - Data serialization

2. **Integration Tests**
   - Test JavaFX application
   - Simulated hangs/crashes
   - Performance impact measurement

3. **Deployment Tests**
   - Windows 10 IoT compatibility
   - Service installation/removal
   - Log rotation

## Change Log Format

### Version 1.0.0 - Initial Release
- [FEATURE] Process monitoring with 60-second intervals
- [FEATURE] Hang detection with 5-second threshold
- [FEATURE] Windows Event Log integration
- [FEATURE] JSON logging with daily rotation
- [SECURITY] Restricted service permissions
- [DEPLOY] MSI installer for Windows 10 IoT