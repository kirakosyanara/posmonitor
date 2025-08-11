# POS Monitor

A Windows service application that monitors JavaFX Point of Sale (POS) applications for performance metrics, hangs, and crashes without requiring any modifications to the target application.

## Current Development Status: Phase 1 - Core Features (In Progress)

### ✅ Implemented Features (Phase 1, Week 1 Complete)

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

### 🚧 In Development (Phase 1, Week 2)

- Async logging queue for better performance
- Resource management and monitoring limits
- Comprehensive test suite

### 📋 Planned Features

- Windows Service wrapper for production deployment
- MSI installer for easy installation
- Security hardening and access controls
- Web dashboard for monitoring (future enhancement)

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

### Quick Test

```bash
# Monitor notepad.exe as a test
python pos-monitor-test.py

# Monitor a specific process
python pos-monitor-core.py "YourApp.exe"
```

### Configuration

Edit `pos-monitor-config.json` to customize:
- Target process name
- Monitoring intervals
- Event log sources and filters
- Log directory location

## Architecture

The monitor uses a multi-threaded architecture with separate threads for:
- Performance metrics collection
- Process existence monitoring  
- UI hang detection
- Windows Event Log monitoring

All data is logged to JSON files for easy parsing and analysis.

## Log Output

Logs are written to `C:\ProgramData\POSMonitor\logs\` in daily JSON files:
- Performance metrics every 60 seconds
- Hang events when detected
- Event log errors and warnings
- Crash details with exit codes

## Development Roadmap

See [development-plan.md](development-plan.md) for the complete development roadmap and timeline.

## License

This project is proprietary software for UniSight POS monitoring.
