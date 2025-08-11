# POS Monitor Service Troubleshooting Guide

## Common Issues and Solutions

### 1. Service Won't Install

**Symptoms:**
- Installation script fails
- "Access denied" errors

**Solutions:**
- Ensure you're running as Administrator
- Check if Python is installed and in PATH
- Verify all required files are present
- Check Windows Event Log for detailed errors

### 2. Service Won't Start

**Symptoms:**
- Service fails to start
- Error 1053: Service did not respond in time
- Service starts then immediately stops

**Solutions:**
- Check configuration file exists at `C:\ProgramData\POSMonitor\pos-monitor-config.json`
- Verify the monitored process name is correct in config
- Check service log at `C:\ProgramData\POSMonitor\logs\service.log`
- Ensure all Python dependencies are installed:
  ```
  pip install -r pos-monitor-requirements.txt
  ```

### 3. No Logs Being Created

**Symptoms:**
- Log directory is empty
- No monitoring data being recorded

**Solutions:**
- Check service is actually running: `sc query POSMonitor`
- Verify log directory permissions
- Check if monitored process exists
- Review service.log for errors

### 4. High Memory/CPU Usage

**Symptoms:**
- Service consuming excessive resources
- System performance degradation

**Solutions:**
- Check configuration intervals (increase if too frequent)
- Review log file sizes (enable rotation if needed)
- Check for memory leaks in service.log
- Restart service to clear any issues

### 5. Service Crashes Frequently

**Symptoms:**
- Service stops unexpectedly
- Recovery actions triggered frequently

**Solutions:**
- Check Windows Event Log for crash details
- Review Python error logs
- Verify no conflicts with antivirus software
- Check for corrupted Python installation

## Diagnostic Commands

### Check Service Status
```batch
sc query POSMonitor
sc qc POSMonitor
```

### View Service Logs
```powershell
Get-Content C:\ProgramData\POSMonitor\logs\service.log -Tail 50
```

### Check Event Log
```powershell
Get-EventLog -LogName Application -Source POSMonitor -Newest 10
```

### Test Configuration
```batch
python pos-monitor-core.py notepad.exe
```

## Log File Locations

- **Service Log**: `C:\ProgramData\POSMonitor\logs\service.log`
- **Monitor Logs**: `C:\ProgramData\POSMonitor\logs\pos_monitor_YYYY-MM-DD.json`
- **Windows Event Log**: Application Log, Source: POSMonitor

## Recovery Procedures

### 1. Complete Service Reset
```batch
net stop POSMonitor
rmdir /S /Q C:\ProgramData\POSMonitor\logs
mkdir C:\ProgramData\POSMonitor\logs
net start POSMonitor
```

### 2. Reinstall Service
```batch
python pos-monitor-service.py remove
python pos-monitor-service.py install
```

### 3. Manual Cleanup
If service is stuck:
1. Open Services (services.msc)
2. Find "POS Application Monitor"
3. Stop the service
4. Open Task Manager
5. End any python.exe processes related to POSMonitor
6. Start the service again

## Performance Tuning

### Reduce Resource Usage
Edit `pos-monitor-config.json`:
```json
{
  "monitor": {
    "performance_interval": 300,  // Increase to 5 minutes
    "self_monitor_interval": 600,  // Increase to 10 minutes
    "max_memory_mb": 30  // Reduce memory limit
  }
}
```

### Optimize Logging
```json
{
  "logging": {
    "batch_size": 100,  // Increase batch size
    "flush_interval": 30,  // Increase flush interval
    "max_file_size_mb": 50  // Reduce file size
  }
}
```

## Contact Support

If issues persist:
1. Collect service.log
2. Export recent Windows Event Log entries
3. Note the exact error messages
4. Document steps to reproduce