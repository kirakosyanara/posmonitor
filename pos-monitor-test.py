"""
Test script for POS Monitor
Run this to test basic monitoring functionality before service deployment
"""

import json
import subprocess
import sys
import time
from pathlib import Path

from pos_monitor_core import POSMonitor


def start_test_process():
    """Start a test process (notepad) to monitor"""
    print("Starting test process (notepad.exe)...")
    process = subprocess.Popen(["notepad.exe"])
    time.sleep(2)  # Give it time to start
    return process


def verify_log_files(log_dir: Path):
    """Check if log files are being created properly"""
    print(f"\nChecking log directory: {log_dir}")
    
    if not log_dir.exists():
        print("ERROR: Log directory does not exist!")
        return False
    
    log_files = list(log_dir.glob("pos_monitor_*.json"))
    if not log_files:
        print("ERROR: No log files found!")
        return False
    
    print(f"Found {len(log_files)} log file(s)")
    
    # Check latest log file
    latest_log = max(log_files, key=lambda p: p.stat().st_mtime)
    print(f"Latest log file: {latest_log.name}")
    
    # Read and display some entries
    print("\nRecent log entries:")
    with open(latest_log, 'r') as f:
        lines = f.readlines()[-10:]  # Last 10 entries
        for line in lines:
            entry = json.loads(line)
            print(f"  [{entry['timestamp']}] {entry['type']}: ", end="")
            if entry['type'] == 'performance':
                metrics = entry['metrics']
                print(f"CPU: {metrics['cpu_percent']}%, "
                      f"Memory: {metrics['memory_rss_mb']}MB")
            else:
                print(json.dumps(entry, indent=2))
    
    return True


def main():
    """Run the test"""
    print("POS Monitor Test Script")
    print("=" * 50)
    
    # Test configuration
    config = {
        "log_dir": "C:/ProgramData/POSMonitor/logs",
        "performance_interval": 5,  # Faster for testing
        "process_check_interval": 2,
        "hang_check_interval": 3,
        "hang_timeout_seconds": 3,
        "monitor_self": True,
        "self_monitor_interval": 10,  # Faster for testing
        "max_memory_mb": 50,
        "max_cpu_percent": 10,
        "event_log": {
            "enabled": True,
            "sources": ["Application", "System"],
            "levels": ["Error", "Warning"],
            "java_keywords": ["java", "exception", "error"]
        },
        "logging": {
            "async_enabled": True,
            "max_file_size_mb": 10,
            "retention_days": 7,
            "batch_size": 10,
            "flush_interval": 2
        }
    }
    
    # Create log directory if it doesn't exist
    log_dir = Path(config["log_dir"])
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Option 1: Monitor an existing process
    if len(sys.argv) > 1:
        process_name = sys.argv[1]
        print(f"Monitoring existing process: {process_name}")
        test_process = None
    else:
        # Option 2: Start notepad for testing
        test_process = start_test_process()
        process_name = "notepad.exe"
        print(f"Monitoring test process: {process_name}")
    
    # Create and start monitor
    monitor = POSMonitor(process_name, config)
    
    try:
        # Run monitor in a separate thread
        import threading
        monitor_thread = threading.Thread(target=monitor.start)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        print("\nMonitor is running. Press Ctrl+C to stop.")
        print("Collecting performance data every 5 seconds...")
        
        # Let it run for a while
        for i in range(6):  # 30 seconds total
            time.sleep(5)
            print(f"Running... ({(i+1)*5} seconds)")
        
        # Verify logs are being created
        verify_log_files(log_dir)
        
        # If we started a test process, terminate it
        if test_process:
            print("\nTerminating test process...")
            test_process.terminate()
            time.sleep(3)  # Give monitor time to detect termination
        
        # Check logs again
        print("\nChecking for termination log...")
        verify_log_files(log_dir)
        
    except KeyboardInterrupt:
        print("\n\nStopping monitor...")
    finally:
        monitor.stop()
        if test_process and test_process.poll() is None:
            test_process.terminate()
    
    print("\nTest completed!")


if __name__ == "__main__":
    main()
