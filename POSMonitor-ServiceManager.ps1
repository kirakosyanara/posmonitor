# POS Monitor Service Management PowerShell Module
# Provides advanced service management capabilities

# Requires administrator privileges
#Requires -RunAsAdministrator

# Service configuration
$ServiceName = "POSMonitor"
$ServiceDisplayName = "POS Application Monitor"
$ConfigPath = "C:\ProgramData\POSMonitor\pos-monitor-config.json"
$LogPath = "C:\ProgramData\POSMonitor\logs"

function Get-POSMonitorStatus {
    <#
    .SYNOPSIS
    Gets detailed status of the POS Monitor service
    #>
    
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    
    if ($null -eq $service) {
        Write-Host "POS Monitor service is not installed" -ForegroundColor Red
        return
    }
    
    Write-Host "POS Monitor Service Status" -ForegroundColor Cyan
    Write-Host "=========================" -ForegroundColor Cyan
    Write-Host "Status: $($service.Status)" -ForegroundColor $(if ($service.Status -eq 'Running') { 'Green' } else { 'Yellow' })
    Write-Host "Start Type: $($service.StartType)"
    
    # Get process information if running
    if ($service.Status -eq 'Running') {
        $process = Get-WmiObject Win32_Service | Where-Object { $_.Name -eq $ServiceName }
        if ($process) {
            Write-Host "Process ID: $($process.ProcessId)"
            
            # Get memory usage
            $proc = Get-Process -Id $process.ProcessId -ErrorAction SilentlyContinue
            if ($proc) {
                $memoryMB = [math]::Round($proc.WorkingSet64 / 1MB, 2)
                Write-Host "Memory Usage: $memoryMB MB"
                Write-Host "CPU Time: $($proc.TotalProcessorTime)"
                Write-Host "Threads: $($proc.Threads.Count)"
            }
        }
    }
    
    # Check configuration
    if (Test-Path $ConfigPath) {
        $config = Get-Content $ConfigPath | ConvertFrom-Json
        Write-Host "`nMonitored Process: $($config.monitor.process_name)" -ForegroundColor Cyan
    }
    
    # Check recent logs
    $today = Get-Date -Format "yyyy-MM-dd"
    $todayLog = Join-Path $LogPath "pos_monitor_$today.json"
    
    if (Test-Path $todayLog) {
        $logSize = (Get-Item $todayLog).Length / 1MB
        Write-Host "`nToday's Log: $([math]::Round($logSize, 2)) MB"
        
        # Count log entries
        $entries = Get-Content $todayLog | Measure-Object -Line
        Write-Host "Log Entries Today: $($entries.Lines)"
    }
}

function Start-POSMonitor {
    <#
    .SYNOPSIS
    Starts the POS Monitor service
    #>
    
    Write-Host "Starting POS Monitor service..." -ForegroundColor Yellow
    Start-Service -Name $ServiceName -ErrorAction Stop
    
    # Wait for service to start
    $timeout = 30
    $elapsed = 0
    
    while ((Get-Service -Name $ServiceName).Status -ne 'Running' -and $elapsed -lt $timeout) {
        Start-Sleep -Seconds 1
        $elapsed++
        Write-Host "." -NoNewline
    }
    
    Write-Host ""
    
    if ((Get-Service -Name $ServiceName).Status -eq 'Running') {
        Write-Host "Service started successfully!" -ForegroundColor Green
    } else {
        Write-Host "Service failed to start within $timeout seconds" -ForegroundColor Red
    }
}

function Stop-POSMonitor {
    <#
    .SYNOPSIS
    Stops the POS Monitor service
    #>
    
    Write-Host "Stopping POS Monitor service..." -ForegroundColor Yellow
    Stop-Service -Name $ServiceName -Force -ErrorAction Stop
    Write-Host "Service stopped" -ForegroundColor Green
}

function Restart-POSMonitor {
    <#
    .SYNOPSIS
    Restarts the POS Monitor service
    #>
    
    Stop-POSMonitor
    Start-Sleep -Seconds 2
    Start-POSMonitor
}

function Get-POSMonitorLogs {
    <#
    .SYNOPSIS
    Retrieves and displays recent log entries
    
    .PARAMETER Count
    Number of log entries to display (default: 10)
    
    .PARAMETER Type
    Filter by log entry type (e.g., 'performance', 'hang', 'crash')
    #>
    
    param(
        [int]$Count = 10,
        [string]$Type = $null
    )
    
    $today = Get-Date -Format "yyyy-MM-dd"
    $todayLog = Join-Path $LogPath "pos_monitor_$today.json"
    
    if (-not (Test-Path $todayLog)) {
        Write-Host "No log file found for today" -ForegroundColor Yellow
        return
    }
    
    Write-Host "Recent Log Entries" -ForegroundColor Cyan
    Write-Host "==================" -ForegroundColor Cyan
    
    $logs = Get-Content $todayLog | Select-Object -Last $Count | ForEach-Object {
        ConvertFrom-Json $_
    }
    
    if ($Type) {
        $logs = $logs | Where-Object { $_.type -eq $Type }
    }
    
    foreach ($log in $logs) {
        $timestamp = [DateTime]::Parse($log.timestamp).ToLocalTime()
        
        switch ($log.type) {
            'performance' {
                Write-Host "[$timestamp] PERFORMANCE - CPU: $($log.metrics.cpu_percent)%, Memory: $($log.metrics.memory_mb) MB" -ForegroundColor Green
            }
            'hang' {
                Write-Host "[$timestamp] HANG DETECTED - Process: $($log.process_name), Duration: $($log.duration_seconds)s" -ForegroundColor Yellow
            }
            'crash' {
                Write-Host "[$timestamp] CRASH - Process: $($log.process_name), Exit Code: $($log.exit_code)" -ForegroundColor Red
            }
            'event_log' {
                Write-Host "[$timestamp] EVENT LOG - Level: $($log.level), Source: $($log.source)" -ForegroundColor Magenta
                Write-Host "  Message: $($log.message.Substring(0, [Math]::Min(100, $log.message.Length)))..." -ForegroundColor Gray
            }
            'monitor_health' {
                Write-Host "[$timestamp] MONITOR HEALTH - CPU: $($log.metrics.cpu_percent)%, Memory: $($log.metrics.memory_mb) MB" -ForegroundColor Cyan
            }
            default {
                Write-Host "[$timestamp] $($log.type.ToUpper())" -ForegroundColor White
            }
        }
    }
}

function Test-POSMonitorHealth {
    <#
    .SYNOPSIS
    Performs a health check on the POS Monitor service
    #>
    
    Write-Host "POS Monitor Health Check" -ForegroundColor Cyan
    Write-Host "=======================" -ForegroundColor Cyan
    
    $issues = @()
    
    # Check service status
    $service = Get-Service -Name $ServiceName -ErrorAction SilentlyContinue
    if ($null -eq $service) {
        $issues += "Service is not installed"
    } elseif ($service.Status -ne 'Running') {
        $issues += "Service is not running"
    }
    
    # Check configuration
    if (-not (Test-Path $ConfigPath)) {
        $issues += "Configuration file missing"
    }
    
    # Check log directory
    if (-not (Test-Path $LogPath)) {
        $issues += "Log directory missing"
    } else {
        # Check disk space
        $drive = (Get-Item $LogPath).Root.Name
        $disk = Get-WmiObject Win32_LogicalDisk -Filter "DeviceID='$drive'"
        $freeGB = [math]::Round($disk.FreeSpace / 1GB, 2)
        
        if ($freeGB -lt 1) {
            $issues += "Low disk space on log drive ($freeGB GB free)"
        }
    }
    
    # Check recent activity
    $today = Get-Date -Format "yyyy-MM-dd"
    $todayLog = Join-Path $LogPath "pos_monitor_$today.json"
    
    if (Test-Path $todayLog) {
        $lastModified = (Get-Item $todayLog).LastWriteTime
        $minutesSinceUpdate = ((Get-Date) - $lastModified).TotalMinutes
        
        if ($minutesSinceUpdate -gt 10) {
            $issues += "No log updates in the last $([int]$minutesSinceUpdate) minutes"
        }
    }
    
    # Report results
    if ($issues.Count -eq 0) {
        Write-Host "✓ All health checks passed" -ForegroundColor Green
    } else {
        Write-Host "✗ Issues found:" -ForegroundColor Red
        foreach ($issue in $issues) {
            Write-Host "  - $issue" -ForegroundColor Yellow
        }
    }
}

function Set-POSMonitorConfig {
    <#
    .SYNOPSIS
    Updates POS Monitor configuration
    
    .PARAMETER ProcessName
    Name of the process to monitor
    
    .PARAMETER PerformanceInterval
    Interval in seconds for performance sampling
    #>
    
    param(
        [string]$ProcessName,
        [int]$PerformanceInterval
    )
    
    if (-not (Test-Path $ConfigPath)) {
        Write-Host "Configuration file not found at $ConfigPath" -ForegroundColor Red
        return
    }
    
    $config = Get-Content $ConfigPath | ConvertFrom-Json
    
    if ($ProcessName) {
        $config.monitor.process_name = $ProcessName
        Write-Host "Updated process name to: $ProcessName"
    }
    
    if ($PerformanceInterval) {
        $config.monitor.performance_interval = $PerformanceInterval
        Write-Host "Updated performance interval to: $PerformanceInterval seconds"
    }
    
    $config | ConvertTo-Json -Depth 10 | Set-Content $ConfigPath
    Write-Host "Configuration saved. Restart the service for changes to take effect." -ForegroundColor Yellow
}

# Export functions
Export-ModuleMember -Function Get-POSMonitorStatus, Start-POSMonitor, Stop-POSMonitor, Restart-POSMonitor, Get-POSMonitorLogs, Test-POSMonitorHealth, Set-POSMonitorConfig

Write-Host "POS Monitor Service Manager loaded" -ForegroundColor Green
Write-Host "Available commands:" -ForegroundColor Cyan
Write-Host "  Get-POSMonitorStatus   - View service status"
Write-Host "  Start-POSMonitor       - Start the service"
Write-Host "  Stop-POSMonitor        - Stop the service"
Write-Host "  Restart-POSMonitor     - Restart the service"
Write-Host "  Get-POSMonitorLogs     - View recent logs"
Write-Host "  Test-POSMonitorHealth  - Run health checks"
Write-Host "  Set-POSMonitorConfig   - Update configuration"