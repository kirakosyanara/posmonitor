# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

POS Application Monitor is a Windows service designed to monitor JavaFX Point of Sale applications for performance metrics, hangs, and crashes without requiring any modifications to the target application. The system is built in Python and runs as a Windows service.

## Key Architecture Components

1. **Core Monitor (`pos-monitor-core.py`)**: Main monitoring class that manages process tracking and metric collection
2. **Configuration (`pos-monitor-config.json`)**: JSON-based configuration for process targeting and monitoring intervals
3. **Test Suite (`pos-monitor-test.py`)**: Testing framework for validating monitoring functionality

## Development Commands

### Setup and Dependencies
```bash
# Install dependencies
pip install -r pos-monitor-requirements.txt
```

### Running and Testing
```bash
# Run monitor for testing (monitors notepad.exe by default)
python pos-monitor-core.py

# Run monitor for specific process
python pos-monitor-core.py "YourPOSApp.exe"

# Run test suite with automated notepad monitoring
python pos-monitor-test.py

# Run test suite for existing process
python pos-monitor-test.py "process_name.exe"
```

### Building Windows Service
The project is designed to be packaged as a Windows service using py2exe or PyInstaller. Service configuration is defined in `pos-monitor-config.json` under the `service` section.

## Code Architecture

### Threading Model
The monitor uses multiple threads for different monitoring tasks:
- **Performance Monitor Thread**: Collects CPU/memory metrics every 60 seconds
- **Process Existence Thread**: Checks if target process is running every 5 seconds
- **Event Log Monitor Thread** (planned): Will monitor Windows Event Logs
- **Hang Detector Thread** (planned): Will detect UI unresponsiveness

### Data Flow
1. Monitor discovers target process by name
2. Metrics are collected at configured intervals
3. All data is logged as JSON to `C:\ProgramData\POSMonitor\logs\`
4. Log files are rotated daily with format: `pos_monitor_YYYY-MM-DD.json`

### Log Entry Types
- `performance`: Regular metrics (CPU, memory, threads)
- `process_started`: Target process discovered
- `process_terminated`: Target process ended
- `monitor_stopped`: Monitor service stopped
- `hang` (planned): UI unresponsiveness detected
- `error` (planned): Application errors from Event Log
- `crash` (planned): Unexpected termination

## Important Configuration

The monitoring behavior is controlled by `pos-monitor-config.json`:
- `process_name`: Target process to monitor
- `performance_interval`: Seconds between metric collections (default: 60)
- `process_check_interval`: Seconds between process existence checks (default: 5)
- `log_dir`: Directory for JSON log files

## Development Notes

1. **Windows-Specific**: This project uses Windows APIs (pywin32) and is designed specifically for Windows 10 IoT
2. **No Process Modification**: The monitor operates completely externally without injecting into or modifying the target process
3. **Security**: Service runs with minimal privileges needed to read process metrics
4. **Resource Efficiency**: Designed to use <50MB memory and minimal CPU