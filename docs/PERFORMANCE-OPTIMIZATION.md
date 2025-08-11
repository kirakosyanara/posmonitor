# POS Monitor Performance Optimization Guide

## Overview

This guide provides recommendations for optimizing POS Monitor's performance and minimizing its impact on monitored applications. Use these techniques to achieve the best balance between monitoring coverage and system resources.

## Performance Metrics

### Resource Usage Targets

| Resource | Idle | Normal | Peak | Maximum |
|----------|------|--------|------|---------|
| CPU | <0.5% | 1-2% | 3-5% | 10% |
| Memory | 30-40 MB | 50-70 MB | 80-100 MB | 150 MB |
| Disk I/O | <100 KB/s | 200-500 KB/s | 1-2 MB/s | 5 MB/s |
| Handles | <100 | 150-200 | 250-300 | 500 |

## Optimization Strategies

### 1. Interval Tuning

Adjust monitoring intervals based on your requirements:

#### Low-Impact Configuration
```json
{
  "monitor": {
    "performance_interval": 300,
    "process_check_interval": 30,
    "hang_detection": {
      "check_interval": 120
    }
  }
}
```
- **Use Case**: Stable production systems
- **Impact**: <0.5% CPU usage
- **Trade-off**: Slower issue detection

#### Balanced Configuration
```json
{
  "monitor": {
    "performance_interval": 60,
    "process_check_interval": 10,
    "hang_detection": {
      "check_interval": 30
    }
  }
}
```
- **Use Case**: Most deployments
- **Impact**: 1-2% CPU usage
- **Trade-off**: Good balance

#### High-Frequency Configuration
```json
{
  "monitor": {
    "performance_interval": 15,
    "process_check_interval": 5,
    "hang_detection": {
      "check_interval": 15
    }
  }
}
```
- **Use Case**: Critical systems, debugging
- **Impact**: 3-5% CPU usage
- **Trade-off**: Higher resource usage

### 2. Logging Optimization

#### Batch Writing
Increase batch size to reduce I/O operations:
```json
{
  "logging": {
    "batch_size": 500,
    "flush_interval_seconds": 30
  }
}
```

#### File Rotation
Optimize rotation for your retention needs:
```json
{
  "logging": {
    "max_file_size_mb": 50,
    "compression_enabled": true,
    "max_files": 14
  }
}
```

#### Disable Debug Logging
In production, always disable debug logs:
```json
{
  "logging": {
    "include_debug": false
  }
}
```

### 3. Thread Pool Optimization

Adjust thread pool based on CPU cores:

#### Single/Dual Core Systems
```json
{
  "advanced": {
    "thread_pool_size": 2,
    "queue_size": 5000
  }
}
```

#### Quad Core Systems
```json
{
  "advanced": {
    "thread_pool_size": 4,
    "queue_size": 10000
  }
}
```

#### Many-Core Systems (8+)
```json
{
  "advanced": {
    "thread_pool_size": 6,
    "queue_size": 20000
  }
}
```

### 4. Event Log Filtering

Reduce event log processing overhead:

```json
{
  "monitor": {
    "event_log": {
      "sources": ["Application"],
      "severity_levels": ["Error"],
      "java_filter_enabled": true
    }
  }
}
```

### 5. Resource Limits

Set appropriate limits to prevent runaway resource usage:

```json
{
  "monitor": {
    "resource_limits": {
      "monitor_max_memory_mb": 100,
      "monitor_max_cpu_percent": 5,
      "warning_threshold_percent": 80
    }
  }
}
```

## Scenario-Based Configurations

### Retail POS Terminal (Limited Resources)
```json
{
  "monitor": {
    "process_name": "RetailPOS.exe",
    "performance_interval": 120,
    "process_check_interval": 20,
    "hang_detection": {
      "enabled": true,
      "check_interval": 60
    },
    "event_log": {
      "enabled": false
    },
    "resource_limits": {
      "monitor_max_memory_mb": 50,
      "monitor_max_cpu_percent": 2
    }
  },
  "logging": {
    "max_file_size_mb": 10,
    "max_files": 7,
    "batch_size": 200,
    "flush_interval_seconds": 30
  },
  "advanced": {
    "thread_pool_size": 2
  }
}
```

### High-Volume Transaction System
```json
{
  "monitor": {
    "process_name": "TransactionServer.exe",
    "performance_interval": 30,
    "process_check_interval": 5,
    "hang_detection": {
      "enabled": true,
      "timeout_seconds": 3,
      "check_interval": 15
    }
  },
  "logging": {
    "max_file_size_mb": 100,
    "batch_size": 1000,
    "flush_interval_seconds": 5,
    "compression_enabled": true
  },
  "advanced": {
    "thread_pool_size": 4,
    "metric_buffer_size": 5000
  }
}
```

### Development/Testing Environment
```json
{
  "monitor": {
    "process_name": "TestPOS.exe",
    "performance_interval": 10,
    "process_check_interval": 2,
    "hang_detection": {
      "timeout_seconds": 2,
      "check_interval": 10
    }
  },
  "logging": {
    "include_debug": true,
    "batch_size": 50,
    "flush_interval_seconds": 1
  },
  "advanced": {
    "enable_profiling": true
  }
}
```

## Performance Monitoring

### Built-in Metrics

Monitor the monitor itself using these metrics:

1. **Resource Usage Logs**
   - Check `pos_monitor_*.json` for `monitor_health` entries
   - Look for CPU and memory usage trends

2. **Windows Performance Counters**
   ```powershell
   # Monitor CPU usage
   Get-Counter "\Process(POSMonitorService)\% Processor Time"
   
   # Monitor memory usage
   Get-Counter "\Process(POSMonitorService)\Working Set - Private"
   ```

3. **Event Log Warnings**
   - Check for resource limit warnings
   - Look for performance degradation alerts

### Performance Baseline

Establish a baseline after deployment:

```powershell
# Collect 1-hour baseline
$baseline = @()
1..60 | ForEach-Object {
    $cpu = (Get-Counter "\Process(POSMonitorService)\% Processor Time").CounterSamples.CookedValue
    $mem = (Get-Counter "\Process(POSMonitorService)\Working Set - Private").CounterSamples.CookedValue / 1MB
    $baseline += [PSCustomObject]@{
        Time = Get-Date
        CPU = $cpu
        MemoryMB = $mem
    }
    Start-Sleep -Seconds 60
}
$baseline | Export-Csv "pos-monitor-baseline.csv"
```

## Troubleshooting Performance Issues

### High CPU Usage

1. **Check Intervals**
   ```powershell
   # View current configuration
   Get-Content "C:\ProgramData\POSMonitor\pos-monitor-config.json" | ConvertFrom-Json
   ```

2. **Increase Intervals**
   - Double performance_interval
   - Increase hang_detection.check_interval
   - Reduce event log monitoring

3. **Check for Loops**
   - Review logs for rapid repeated entries
   - Verify target process name is correct

### High Memory Usage

1. **Check Queue Sizes**
   - Look for queue overflow warnings
   - Reduce queue_size in advanced settings

2. **Reduce Buffering**
   ```json
   {
     "logging": {
       "batch_size": 100
     },
     "advanced": {
       "metric_buffer_size": 500
     }
   }
   ```

3. **Enable Compression**
   - Set compression_enabled to true
   - Reduce max_files count

### High Disk I/O

1. **Increase Batch Size**
   ```json
   {
     "logging": {
       "batch_size": 1000,
       "flush_interval_seconds": 60
     }
   }
   ```

2. **Reduce Logging Frequency**
   - Increase performance_interval
   - Disable debug logging

3. **Use SSD Storage**
   - Move logs to SSD if available
   - Consider RAM disk for extreme cases

## Best Practices

### DO:
- ✅ Start with default configuration
- ✅ Monitor resource usage after changes
- ✅ Test changes in non-production first
- ✅ Document custom configurations
- ✅ Use compression for long-term storage
- ✅ Set appropriate resource limits

### DON'T:
- ❌ Set intervals below 10 seconds without testing
- ❌ Disable all monitoring to save resources
- ❌ Use debug logging in production
- ❌ Ignore resource warnings
- ❌ Set queue sizes too small

## Advanced Techniques

### CPU Affinity
Set CPU affinity to isolate monitor from critical processes:
```powershell
# Set to use only CPU 0
$process = Get-Process POSMonitorService
$process.ProcessorAffinity = 1
```

### Priority Adjustment
Lower process priority for background operation:
```cmd
wmic process where name="POSMonitorService.exe" CALL setpriority "below normal"
```

### Memory Working Set
Trim working set during idle periods:
```python
# Add to monitor code
import win32api
import win32process

def trim_memory():
    """Trim working set during idle periods"""
    handle = win32api.GetCurrentProcess()
    win32process.SetProcessWorkingSetSize(handle, -1, -1)
```

## Capacity Planning

### Estimating Log Storage

```
Daily Log Size = (Metrics/Hour × 24) × Average Entry Size

Where:
- Metrics/Hour = 3600 / performance_interval
- Average Entry Size ≈ 500 bytes

Example (60-second interval):
- Metrics/Hour = 60
- Daily entries = 1,440
- Daily size = 1,440 × 500 bytes = 720 KB
- Monthly size = 21.6 MB (uncompressed)
- Monthly size = ~2 MB (compressed)
```

### Scaling Recommendations

| Monitored Processes | Recommended Config | Resource Impact |
|--------------------|--------------------|-----------------|
| 1 | Default | 50 MB RAM, 1% CPU |
| 2-5 | Increase threads to 4 | 80 MB RAM, 2% CPU |
| 5-10 | Dedicated monitoring server | 150 MB RAM, 3% CPU |
| 10+ | Multiple monitor instances | Varies |

## Validation Checklist

After optimization:

- [ ] CPU usage within targets
- [ ] Memory usage stable
- [ ] No queue overflow warnings
- [ ] Logs rotating properly
- [ ] Monitoring objectives still met
- [ ] No missed events or metrics
- [ ] Service stable over 24 hours

## Summary

Effective performance optimization requires:
1. Understanding your monitoring requirements
2. Starting with appropriate baseline configuration
3. Measuring actual resource usage
4. Adjusting incrementally
5. Validating changes don't compromise monitoring

Remember: The goal is finding the right balance between comprehensive monitoring and minimal system impact.