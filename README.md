# POS Monitor

A Windows service application that monitors JavaFX Point of Sale (POS) applications for performance metrics, hangs, and crashes without requiring any modifications to the target application.

## Current Development Status: Phase 1 Complete ✅

### Implemented Features (Phase 1 - Core Monitoring)

#### Week 1: Core Monitoring Features
1. **Performance Monitoring**
   - CPU and memory usage tracking
   - Thread and handle count monitoring
   - Configurable sampling intervals (default: 60 seconds)

2. **Hang Detection** 
   - UI responsiveness checking using Windows SendMessageTimeout API
   - JavaFX window discovery and monitoring
   - Configurable timeout threshold (default: 5 seconds)
   - Automatic recovery detection

3. **Event Log Integration**
   - Windows Application and System event log monitoring
   - Java-specific error pattern matching
   - Filters for process name and severity levels
   - Captures OutOfMemoryError, StackOverflowError, etc.

4. **Enhanced Crash Detection**
   - Exit code interpretation (Windows and Java-specific)
   - Crash context collection (uptime, last metrics)
   - Differentiation between crashes and normal termination

#### Week 2: Robustness & Performance
5. **Async Logging System**
   - Thread-safe queue with batched writes
   - Automatic log rotation by size with compression
   - Configurable retention period with old file cleanup
   - High-performance with minimal I/O blocking

6. **Self-Monitoring**
   - Monitor tracks its own resource usage
   - Configurable CPU and memory limits
   - Warnings when limits are exceeded
   - Automatic garbage collection on high memory

7. **Comprehensive Testing**
   - Unit tests for all major components
   - Integration tests for full monitoring cycle
   - Mock-based testing for Windows APIs
   - Test runner with coverage analysis

### 🚧 Next Phase: Windows Service Implementation (Phase 2)

- Windows Service wrapper using win32serviceutil
- Service installation and management scripts
- Auto-start and recovery configuration
- MSI installer for production deployment

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

## Testing the Application

### Prerequisites

- Windows 10 or later
- Python 3.8+ 
- Administrator privileges (for event log access)
- Required packages: `pip install -r pos-monitor-requirements.txt`

### Quick Test

```bash
# Monitor notepad.exe as a test
python pos-monitor-test.py

# Monitor a specific process
python pos-monitor-core.py "YourApp.exe"

# Run unit tests
python run_tests.py

# Run tests with coverage report
python run_tests.py --coverage
```

### Configuration

Edit `pos-monitor-config.json` to customize:
- Target process name
- Monitoring intervals  
- Event log sources and filters
- Log directory location
- Async logging settings
- Resource limits

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

## Development Roadmap

See [development-plan.md](development-plan.md) for the complete development roadmap and timeline.

## License

This project is proprietary software for UniSight POS monitoring.
