# POS Monitor Configuration Reference

## Overview

POS Monitor uses a JSON configuration file located at `C:\ProgramData\POSMonitor\pos-monitor-config.json`. This document provides a complete reference for all configuration options.

## Configuration File Location

- **Primary**: `C:\ProgramData\POSMonitor\pos-monitor-config.json`
- **Fallback**: `<InstallDir>\pos-monitor-config.json`
- **Template**: `<InstallDir>\pos-monitor-config.template.json`

## Configuration Structure

```json
{
  "monitor": {
    "process_name": "string",
    "performance_interval": number,
    "process_check_interval": number,
    "hang_detection": {
      "enabled": boolean,
      "timeout_seconds": number,
      "check_interval": number,
      "retry_count": number
    },
    "event_log": {
      "enabled": boolean,
      "sources": ["Application", "System"],
      "java_filter_enabled": boolean,
      "severity_levels": ["Error", "Warning"]
    },
    "resource_limits": {
      "monitor_max_memory_mb": number,
      "monitor_max_cpu_percent": number,
      "warning_threshold_percent": number
    }
  },
  "logging": {
    "log_dir": "string",
    "file_prefix": "string",
    "max_file_size_mb": number,
    "max_files": number,
    "retention_days": number,
    "compression_enabled": boolean,
    "batch_size": number,
    "flush_interval_seconds": number,
    "include_debug": boolean
  },
  "service": {
    "restart_on_failure": boolean,
    "restart_delay_seconds": number,
    "max_restart_attempts": number,
    "health_check_interval": number
  },
  "advanced": {
    "thread_pool_size": number,
    "queue_size": number,
    "metric_buffer_size": number,
    "enable_profiling": boolean
  }
}
```

## Configuration Sections

### Monitor Section

Controls core monitoring behavior.

#### process_name
- **Type**: string
- **Required**: Yes
- **Default**: None
- **Description**: Name of the process to monitor (e.g., "MyPOSApp.exe")
- **Example**: `"process_name": "JavaPOS.exe"`

#### performance_interval
- **Type**: integer
- **Required**: No
- **Default**: 60
- **Range**: 10-3600
- **Description**: Seconds between performance metric collections
- **Example**: `"performance_interval": 30`

#### process_check_interval
- **Type**: integer
- **Required**: No
- **Default**: 5
- **Range**: 1-60
- **Description**: Seconds between process existence checks
- **Example**: `"process_check_interval": 10`

#### hang_detection
Configures UI hang detection for JavaFX applications.

```json
"hang_detection": {
  "enabled": true,
  "timeout_seconds": 5,
  "check_interval": 30,
  "retry_count": 3
}
```

- **enabled**: Enable/disable hang detection (default: true)
- **timeout_seconds**: Seconds to wait for UI response (default: 5, range: 1-30)
- **check_interval**: Seconds between hang checks (default: 30, range: 10-300)
- **retry_count**: Retries before declaring hang (default: 3, range: 1-10)

#### event_log
Configures Windows Event Log monitoring.

```json
"event_log": {
  "enabled": true,
  "sources": ["Application", "System"],
  "java_filter_enabled": true,
  "severity_levels": ["Error", "Warning"]
}
```

- **enabled**: Enable/disable event log monitoring (default: true)
- **sources**: Event logs to monitor (default: ["Application", "System"])
- **java_filter_enabled**: Filter for Java-related events (default: true)
- **severity_levels**: Event types to capture (default: ["Error", "Warning"])

#### resource_limits
Sets resource usage limits for the monitor itself.

```json
"resource_limits": {
  "monitor_max_memory_mb": 100,
  "monitor_max_cpu_percent": 5,
  "warning_threshold_percent": 80
}
```

- **monitor_max_memory_mb**: Max memory for monitor (default: 100, range: 50-500)
- **monitor_max_cpu_percent**: Max CPU usage (default: 5, range: 1-20)
- **warning_threshold_percent**: Warning threshold (default: 80, range: 50-95)

### Logging Section

Controls log file behavior and performance.

#### Basic Settings

```json
"logging": {
  "log_dir": "C:\\ProgramData\\POSMonitor\\logs",
  "file_prefix": "pos_monitor",
  "include_debug": false
}
```

- **log_dir**: Directory for log files (default: "C:\\ProgramData\\POSMonitor\\logs")
- **file_prefix**: Log file name prefix (default: "pos_monitor")
- **include_debug**: Include debug-level logs (default: false)

#### File Management

```json
"logging": {
  "max_file_size_mb": 10,
  "max_files": 30,
  "retention_days": 30,
  "compression_enabled": true
}
```

- **max_file_size_mb**: Max size before rotation (default: 10, range: 1-100)
- **max_files**: Maximum number of log files (default: 30, range: 5-365)
- **retention_days**: Days to keep logs (default: 30, range: 1-365)
- **compression_enabled**: Compress rotated logs (default: true)

#### Performance Settings

```json
"logging": {
  "batch_size": 100,
  "flush_interval_seconds": 5
}
```

- **batch_size**: Logs to batch before writing (default: 100, range: 10-1000)
- **flush_interval_seconds**: Max seconds between flushes (default: 5, range: 1-60)

### Service Section

Controls Windows service behavior.

```json
"service": {
  "restart_on_failure": true,
  "restart_delay_seconds": 60,
  "max_restart_attempts": 3,
  "health_check_interval": 300
}
```

- **restart_on_failure**: Auto-restart on failure (default: true)
- **restart_delay_seconds**: Delay between restarts (default: 60, range: 10-600)
- **max_restart_attempts**: Max restart attempts (default: 3, range: 0-10)
- **health_check_interval**: Health check frequency (default: 300, range: 60-3600)

### Advanced Section

Advanced performance tuning options.

```json
"advanced": {
  "thread_pool_size": 4,
  "queue_size": 10000,
  "metric_buffer_size": 1000,
  "enable_profiling": false
}
```

- **thread_pool_size**: Worker thread count (default: 4, range: 2-16)
- **queue_size**: Max queued items (default: 10000, range: 1000-100000)
- **metric_buffer_size**: Metric buffer size (default: 1000, range: 100-10000)
- **enable_profiling**: Enable performance profiling (default: false)

## Configuration Examples

### Minimal Configuration

```json
{
  "monitor": {
    "process_name": "MyPOS.exe"
  }
}
```

### High-Frequency Monitoring

```json
{
  "monitor": {
    "process_name": "CriticalPOS.exe",
    "performance_interval": 15,
    "process_check_interval": 2,
    "hang_detection": {
      "enabled": true,
      "timeout_seconds": 3,
      "check_interval": 15
    }
  },
  "logging": {
    "batch_size": 50,
    "flush_interval_seconds": 2
  }
}
```

### Long-Term Storage

```json
{
  "monitor": {
    "process_name": "RetailPOS.exe",
    "performance_interval": 300
  },
  "logging": {
    "max_file_size_mb": 50,
    "max_files": 365,
    "retention_days": 365,
    "compression_enabled": true
  }
}
```

### Resource-Constrained System

```json
{
  "monitor": {
    "process_name": "LitePOS.exe",
    "performance_interval": 120,
    "resource_limits": {
      "monitor_max_memory_mb": 50,
      "monitor_max_cpu_percent": 2
    }
  },
  "logging": {
    "max_file_size_mb": 5,
    "max_files": 7,
    "batch_size": 200,
    "flush_interval_seconds": 10
  },
  "advanced": {
    "thread_pool_size": 2,
    "queue_size": 5000
  }
}
```

## Environment Variables

Configuration values can be overridden using environment variables:

- `POSMONITOR_CONFIG_PATH`: Override config file location
- `POSMONITOR_LOG_DIR`: Override log directory
- `POSMONITOR_PROCESS_NAME`: Override monitored process name
- `POSMONITOR_DEBUG`: Enable debug logging (set to "true")

Example:
```cmd
set POSMONITOR_PROCESS_NAME=AlternativePOS.exe
set POSMONITOR_DEBUG=true
net start POSMonitor
```

## Configuration Validation

The service validates configuration on startup. Invalid settings will:
1. Log an error to Windows Event Log
2. Use default values where possible
3. Prevent service start for critical errors

Common validation errors:
- Invalid JSON syntax
- Out-of-range numeric values
- Missing required fields
- Invalid file paths

## Dynamic Configuration

Some settings can be changed without restarting the service:
- Log levels (via `include_debug`)
- Performance intervals (applied on next cycle)

To reload configuration:
```powershell
# Using PowerShell module
Import-Module "C:\Program Files\UniSight\POS Monitor\POSMonitor-ServiceManager.ps1"
Restart-POSMonitorService
```

## Best Practices

1. **Start with Defaults**: Modify only what's needed
2. **Test Changes**: Validate in test environment first
3. **Monitor Impact**: Check resource usage after changes
4. **Document Changes**: Keep notes on customizations
5. **Backup Config**: Save working configurations

## Troubleshooting Configuration

### Service Won't Start
- Check JSON syntax using online validator
- Review Windows Event Log for specific errors
- Ensure all paths exist and are accessible

### High Resource Usage
- Increase intervals
- Reduce batch sizes
- Enable compression
- Limit retention period

### Missing Metrics
- Verify process name matches exactly
- Check hang detection timeout isn't too short
- Ensure event log sources are accessible

## Security Considerations

1. **File Permissions**: Config file should be readable only by:
   - SYSTEM
   - Administrators
   
2. **Sensitive Data**: Never store passwords or keys in config

3. **Path Validation**: Use absolute paths to prevent hijacking

## Migration Guide

When upgrading from previous versions:

1. Backup existing configuration
2. Install new version
3. Merge custom settings into new config
4. Validate with test run
5. Deploy to production

## Reference Commands

### View Current Configuration
```powershell
Get-Content "C:\ProgramData\POSMonitor\pos-monitor-config.json" | ConvertFrom-Json | ConvertTo-Json -Depth 10
```

### Validate Configuration
```powershell
try {
    $config = Get-Content "C:\ProgramData\POSMonitor\pos-monitor-config.json" | ConvertFrom-Json
    Write-Host "Configuration is valid"
} catch {
    Write-Error "Invalid configuration: $_"
}
```

### Reset to Defaults
```cmd
copy "C:\Program Files\UniSight\POS Monitor\pos-monitor-config.json" ^
     "C:\ProgramData\POSMonitor\pos-monitor-config.json" /Y
```