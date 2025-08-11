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

try:
    from pos_monitor_hang_detector import HangDetector
except ImportError:
    HangDetector = None
    logging.warning("Hang detector module not available - hang detection disabled")

try:
    from pos_monitor_event_log import EventLogMonitor
except ImportError:
    EventLogMonitor = None
    logging.warning("Event log module not available - event log monitoring disabled")


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
        self.hang_check_interval = config.get("hang_check_interval", 5)  # seconds
        
        # Initialize hang detector if available
        self.hang_detector = None
        if HangDetector:
            hang_timeout = config.get("hang_timeout_seconds", 5)
            self.hang_detector = HangDetector(timeout_seconds=hang_timeout)
            self.logger.info(f"Hang detection enabled with {hang_timeout}s timeout")
        else:
            self.logger.warning("Hang detection not available")
        
        # Initialize event log monitor if available
        self.event_log_monitor = None
        if EventLogMonitor and config.get("event_log", {}).get("enabled", True):
            self.event_log_monitor = EventLogMonitor(process_name, config.get("event_log", {}))
            self.logger.info("Event log monitoring enabled")
        else:
            self.logger.warning("Event log monitoring not available")
        
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
    
    def get_crash_context(self) -> Dict[str, Any]:
        """Gather context information when a crash is detected"""
        context = {}
        
        try:
            # Get last known metrics
            metrics = self.get_process_metrics()
            if metrics:
                context["last_metrics"] = metrics
            
            # Get process creation time and calculate uptime
            if hasattr(self.target_process, 'create_time'):
                create_time = datetime.fromtimestamp(self.target_process.create_time())
                uptime = (datetime.now() - create_time).total_seconds()
                context["uptime_seconds"] = round(uptime, 2)
                context["create_time"] = create_time.isoformat()
        except:
            pass
        
        return context
    
    def interpret_exit_code(self, exit_code: Optional[int]) -> Dict[str, Any]:
        """Interpret Windows exit codes to provide crash information"""
        if exit_code is None:
            return {"description": "Unknown exit code"}
        
        # Common Windows exit codes
        known_codes = {
            0: {"type": "normal", "description": "Normal termination"},
            1: {"type": "error", "description": "General error"},
            -1: {"type": "error", "description": "Abnormal termination"},
            -1073741510: {"type": "crash", "description": "CTRL+C termination"},
            -1073741819: {"type": "crash", "description": "Access violation (0xC0000005)"},
            -1073741571: {"type": "crash", "description": "Stack overflow (0xC00000FD)"},
            -1073741676: {"type": "crash", "description": "Integer division by zero (0xC0000094)"},
            -1073741795: {"type": "crash", "description": "Illegal instruction (0xC000001D)"},
            -1073741818: {"type": "crash", "description": "Cannot continue execution (0xC0000006)"},
            -1073740791: {"type": "crash", "description": "Memory allocation failure (0xC0000409)"},
            -805306369: {"type": "crash", "description": "Java OutOfMemoryError"},
        }
        
        if exit_code in known_codes:
            return known_codes[exit_code]
        elif exit_code < 0:
            # Negative codes usually indicate crashes
            return {
                "type": "crash",
                "description": f"Abnormal termination (0x{exit_code & 0xFFFFFFFF:08X})"
            }
        else:
            return {
                "type": "error",
                "description": f"Process exited with code {exit_code}"
            }
    
    def handle_process_lost(self):
        """Handle when target process is lost"""
        if self.target_process:
            exit_code = None
            crash_context = {}
            
            try:
                # Gather crash context before process object becomes invalid
                crash_context = self.get_crash_context()
                
                # Try to get exit code
                exit_code = self.target_process.wait(timeout=0)
            except:
                pass
            
            # Interpret exit code
            exit_info = self.interpret_exit_code(exit_code)
            
            # Determine log type based on exit code
            log_type = "crash" if exit_info.get("type") == "crash" else "process_terminated"
            
            # Log process termination
            log_entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "type": log_type,
                "process_name": self.process_name,
                "pid": self.target_process.pid,
                "exit_code": exit_code,
                "exit_info": exit_info,
                "context": crash_context
            }
            
            self.write_log_entry(log_entry)
            
            # Log appropriate message
            if exit_info.get("type") == "crash":
                self.logger.error(f"Process CRASHED: {exit_info['description']} (exit code: {exit_code})")
            else:
                self.logger.warning(f"Process terminated: {exit_info['description']} (exit code: {exit_code})")
            
            self.target_process = None
    
    def monitor_hang_detection(self):
        """Thread function for hang detection monitoring"""
        if not self.hang_detector:
            return
            
        self.logger.info("Starting hang detection monitoring thread")
        
        while not self.stop_event.is_set():
            if self.target_process:
                try:
                    # Check if process is responsive
                    hang_info = self.hang_detector.check_process_responsiveness(
                        self.target_process.pid,
                        self.process_name
                    )
                    
                    if hang_info:
                        # Log hang event
                        self.write_log_entry(hang_info)
                        
                        # Log different messages based on hang state
                        if hang_info["type"] == "hang":
                            self.logger.warning(f"Process hang detected: {self.process_name} (PID: {self.target_process.pid})")
                        elif hang_info["type"] == "hang_recovery":
                            self.logger.info(f"Process recovered from hang: {self.process_name} (PID: {self.target_process.pid}), duration: {hang_info['duration_seconds']}s")
                        
                except Exception as e:
                    self.logger.error(f"Error in hang detection: {e}")
            
            # Wait for next check interval
            self.stop_event.wait(self.hang_check_interval)
    
    def monitor_event_logs(self):
        """Thread function for event log monitoring"""
        if not self.event_log_monitor:
            return
            
        self.logger.info("Starting event log monitoring thread")
        
        # Event log check interval (30 seconds)
        event_log_interval = 30
        
        while not self.stop_event.is_set():
            try:
                # Check for new events
                events = self.event_log_monitor.check_event_logs()
                
                # Log each event
                for event in events:
                    self.write_log_entry(event)
                    
                    # Log summary based on severity
                    if event["level"] == "Error":
                        self.logger.error(f"Event log error: {event['source']} - {event['message'][:100]}...")
                    elif event["level"] == "Warning":
                        self.logger.warning(f"Event log warning: {event['source']} - {event['message'][:100]}...")
                    
            except Exception as e:
                self.logger.error(f"Error in event log monitoring: {e}")
            
            # Wait for next check interval
            self.stop_event.wait(event_log_interval)
    
    def start(self):
        """Start all monitoring threads"""
        self.logger.info(f"Starting POS Monitor for process: {self.process_name}")
        
        # Create monitoring threads
        threads = [
            Thread(target=self.monitor_performance, name="PerformanceMonitor"),
            Thread(target=self.monitor_process_existence, name="ProcessExistenceMonitor")
        ]
        
        # Add hang detection thread if available
        if self.hang_detector:
            threads.append(Thread(target=self.monitor_hang_detection, name="HangDetector"))
        
        # Add event log monitor thread if available
        if self.event_log_monitor:
            threads.append(Thread(target=self.monitor_event_logs, name="EventLogMonitor"))
        
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
    # Try to load config from file, fall back to defaults
    import json
    from pathlib import Path
    
    config_file = Path("pos-monitor-config.json")
    if config_file.exists():
        with open(config_file, 'r') as f:
            full_config = json.load(f)
            config = full_config.get("monitor", {})
            config["event_log"] = full_config.get("event_log", {})
    else:
        config = {
            "log_dir": "C:/ProgramData/POSMonitor/logs",
            "performance_interval": 60,
            "process_check_interval": 5,
            "hang_check_interval": 5,
            "hang_timeout_seconds": 5,
            "event_log": {
                "enabled": True,
                "sources": ["Application", "System"],
                "levels": ["Error", "Warning", "Critical"],
                "java_keywords": ["java", "jvm", "javafx", "exception", "error"]
            }
        }
    
    # Get process name from command line or use default
    import sys
    process_name = sys.argv[1] if len(sys.argv) > 1 else "notepad.exe"
    
    monitor = POSMonitor(process_name, config)
    monitor.start()


if __name__ == "__main__":
    main()
