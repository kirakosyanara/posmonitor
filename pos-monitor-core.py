"""
POS Application Monitor - Core Module
Version: 1.0.0
Purpose: Monitor JavaFX POS application performance without modification
"""

import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from threading import Thread, Event
from typing import Dict, Optional, Any

import psutil


class POSMonitor:
    """Main monitoring class for POS application"""
    
    def __init__(self, process_name: str, config: Dict[str, Any]):
        """
        Initialize the POS Monitor
        
        Args:
            process_name: Name of the process to monitor (e.g., "YourPOSApp.exe")
            config: Configuration dictionary
        """
        self.process_name = process_name
        self.config = config
        self.target_process: Optional[psutil.Process] = None
        self.stop_event = Event()
        self.logger = self._setup_logging()
        
        # Configure paths
        self.log_dir = Path(config.get("log_dir", "C:/ProgramData/POSMonitor/logs"))
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Monitoring intervals
        self.performance_interval = config.get("performance_interval", 60)  # seconds
        self.process_check_interval = config.get("process_check_interval", 5)  # seconds
        
    def _setup_logging(self) -> logging.Logger:
        """Setup Python logging for debugging"""
        logger = logging.getLogger("POSMonitor")
        logger.setLevel(logging.DEBUG)
        
        # Console handler for service debugging
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
        return logger
    
    def find_target_process(self) -> Optional[psutil.Process]:
        """Find the target process by name"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if proc.info['name'].lower() == self.process_name.lower():
                    self.logger.info(f"Found target process: {proc.info['name']} (PID: {proc.info['pid']})")
                    return proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None
    
    def get_process_metrics(self) -> Optional[Dict[str, Any]]:
        """Collect current process metrics"""
        if not self.target_process:
            return None
            
        try:
            # Check if process still exists
            if not self.target_process.is_running():
                return None
            
            # Collect metrics
            with self.target_process.oneshot():
                cpu_percent = self.target_process.cpu_percent(interval=1.0)
                memory_info = self.target_process.memory_info()
                memory_percent = self.target_process.memory_percent()
                
                metrics = {
                    "cpu_percent": round(cpu_percent, 2),
                    "memory_rss_mb": round(memory_info.rss / 1024 / 1024, 2),
                    "memory_vms_mb": round(memory_info.vms / 1024 / 1024, 2),
                    "memory_percent": round(memory_percent, 2),
                    "thread_count": self.target_process.num_threads(),
                    "handle_count": self.target_process.num_handles() if hasattr(self.target_process, 'num_handles') else None
                }
                
            return metrics
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            self.logger.error(f"Error accessing process: {e}")
            return None
    
    def write_log_entry(self, entry: Dict[str, Any]):
        """Write a log entry to JSON file"""
        # Create daily log file
        today = datetime.now().strftime("%Y-%m-%d")
        log_file = self.log_dir / f"pos_monitor_{today}.json"
        
        # Ensure timestamp is in ISO format
        if 'timestamp' not in entry:
            entry['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        # Append to log file
        with open(log_file, 'a', encoding='utf-8') as f:
            json.dump(entry, f)
            f.write('\n')
    
    def monitor_performance(self):
        """Thread function for performance monitoring"""
        self.logger.info("Starting performance monitoring thread")
        
        while not self.stop_event.is_set():
            if self.target_process:
                metrics = self.get_process_metrics()
                
                if metrics:
                    log_entry = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "type": "performance",
                        "process_name": self.process_name,
                        "pid": self.target_process.pid,
                        "metrics": metrics
                    }
                    
                    self.write_log_entry(log_entry)
                    self.logger.debug(f"Logged performance metrics: {metrics}")
                else:
                    # Process might have terminated
                    self.handle_process_lost()
            
            # Wait for next interval
            self.stop_event.wait(self.performance_interval)
    
    def monitor_process_existence(self):
        """Thread function to check if process exists"""
        self.logger.info("Starting process existence monitoring thread")
        
        while not self.stop_event.is_set():
            if not self.target_process:
                # Try to find the process
                self.target_process = self.find_target_process()
                
                if self.target_process:
                    # Log process started
                    log_entry = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "type": "process_started",
                        "process_name": self.process_name,
                        "pid": self.target_process.pid
                    }
                    self.write_log_entry(log_entry)
            else:
                # Check if process still exists
                try:
                    if not self.target_process.is_running():
                        self.handle_process_lost()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    self.handle_process_lost()
            
            self.stop_event.wait(self.process_check_interval)
    
    def handle_process_lost(self):
        """Handle when target process is lost"""
        if self.target_process:
            try:
                # Try to get exit code
                exit_code = self.target_process.wait(timeout=0)
            except:
                exit_code = None
            
            # Log process termination
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": "process_terminated",
                "process_name": self.process_name,
                "pid": self.target_process.pid,
                "exit_code": exit_code
            }
            self.write_log_entry(log_entry)
            self.logger.warning(f"Target process terminated with exit code: {exit_code}")
            
            self.target_process = None
    
    def start(self):
        """Start all monitoring threads"""
        self.logger.info(f"Starting POS Monitor for process: {self.process_name}")
        
        # Create monitoring threads
        threads = [
            Thread(target=self.monitor_performance, name="PerformanceMonitor"),
            Thread(target=self.monitor_process_existence, name="ProcessExistenceMonitor")
        ]
        
        # Start all threads
        for thread in threads:
            thread.daemon = True
            thread.start()
            self.logger.info(f"Started thread: {thread.name}")
        
        # Keep main thread alive
        try:
            while not self.stop_event.is_set():
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("Received interrupt signal")
        
        self.stop()
    
    def stop(self):
        """Stop all monitoring threads"""
        self.logger.info("Stopping POS Monitor")
        self.stop_event.set()
        
        # Log monitor stopped
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "monitor_stopped",
            "process_name": self.process_name
        }
        self.write_log_entry(log_entry)


def main():
    """Main entry point for testing"""
    config = {
        "log_dir": "C:/ProgramData/POSMonitor/logs",
        "performance_interval": 60,
        "process_check_interval": 5
    }
    
    # Get process name from command line or use default
    import sys
    process_name = sys.argv[1] if len(sys.argv) > 1 else "notepad.exe"
    
    monitor = POSMonitor(process_name, config)
    monitor.start()


if __name__ == "__main__":
    main()
