"""
POS Monitor Windows Service
Runs the POS Monitor as a Windows service with auto-start and recovery
"""

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys
import os
import logging
import json
import time
from pathlib import Path
from threading import Thread, Event

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pos_monitor_core import POSMonitor


class POSMonitorService(win32serviceutil.ServiceFramework):
    """Windows Service wrapper for POS Monitor"""
    
    # Service name and display name
    _svc_name_ = "POSMonitor"
    _svc_display_name_ = "POS Application Monitor"
    _svc_description_ = "Monitors POS application performance, hangs, and crashes"
    
    def __init__(self, args):
        """Initialize the service"""
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        
        # Service state
        self.monitor = None
        self.monitor_thread = None
        self.is_running = False
        
        # Set up logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Configure logging for the service"""
        # Log to Windows Event Log and file
        log_dir = Path("C:/ProgramData/POSMonitor/logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # File handler for detailed logs
        log_file = log_dir / "service.log"
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        
        # Format for file logs
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Configure root logger
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        
        self.logger = logging.getLogger("POSMonitorService")
        
    def SvcStop(self):
        """Stop the service"""
        self.logger.info("Service stop requested")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        
        # Signal stop
        self.is_running = False
        win32event.SetEvent(self.hWaitStop)
        
        # Stop the monitor
        if self.monitor:
            self.monitor.stop()
        
        # Wait for monitor thread to finish
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=30)
        
        self.logger.info("Service stopped")
        
    def SvcDoRun(self):
        """Main service entry point"""
        try:
            # Log service start to Windows Event Log
            servicemanager.LogMsg(
                servicemanager.EVENTLOG_INFORMATION_TYPE,
                servicemanager.PYS_SERVICE_STARTED,
                (self._svc_name_, '')
            )
            
            self.logger.info("Service starting...")
            self.is_running = True
            
            # Load configuration
            config = self._load_configuration()
            
            # Start monitor in a separate thread
            self.monitor_thread = Thread(
                target=self._run_monitor,
                args=(config,),
                name="MonitorMain"
            )
            self.monitor_thread.start()
            
            # Wait for stop signal
            win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
            
        except Exception as e:
            self.logger.error(f"Service error: {e}", exc_info=True)
            servicemanager.LogErrorMsg(f"POSMonitor service error: {e}")
            
    def _load_configuration(self):
        """Load service configuration"""
        config_file = Path("C:/ProgramData/POSMonitor/pos-monitor-config.json")
        
        # Try program directory if not in ProgramData
        if not config_file.exists():
            config_file = Path(__file__).parent / "pos-monitor-config.json"
        
        if config_file.exists():
            self.logger.info(f"Loading configuration from {config_file}")
            with open(config_file, 'r') as f:
                full_config = json.load(f)
                config = full_config.get("monitor", {})
                config["event_log"] = full_config.get("event_log", {})
                config["logging"] = full_config.get("logging", {})
                return config
        else:
            self.logger.warning("Configuration file not found, using defaults")
            return self._get_default_config()
    
    def _get_default_config(self):
        """Get default configuration"""
        return {
            "process_name": "YourPOSApp.exe",
            "log_dir": "C:/ProgramData/POSMonitor/logs",
            "performance_interval": 60,
            "process_check_interval": 5,
            "hang_check_interval": 5,
            "hang_timeout_seconds": 5,
            "monitor_self": True,
            "self_monitor_interval": 300,
            "max_memory_mb": 50,
            "max_cpu_percent": 5,
            "event_log": {
                "enabled": True,
                "sources": ["Application", "System"],
                "levels": ["Error", "Warning", "Critical"],
                "java_keywords": ["java", "jvm", "javafx", "exception", "error"]
            },
            "logging": {
                "async_enabled": True,
                "max_file_size_mb": 100,
                "retention_days": 30,
                "batch_size": 50,
                "flush_interval": 5
            }
        }
    
    def _run_monitor(self, config):
        """Run the monitor in a separate thread"""
        try:
            # Get process name from config
            process_name = config.get("process_name", "YourPOSApp.exe")
            self.logger.info(f"Starting monitor for process: {process_name}")
            
            # Create and start monitor
            self.monitor = POSMonitor(process_name, config)
            
            # Run monitor (this blocks until stopped)
            self.monitor.start()
            
        except Exception as e:
            self.logger.error(f"Monitor error: {e}", exc_info=True)
            
            # Try to restart after a delay
            if self.is_running:
                self.logger.info("Attempting to restart monitor in 60 seconds...")
                time.sleep(60)
                
                # Recursive restart attempt
                if self.is_running:
                    self._run_monitor(config)


def install_service():
    """Install the Windows service"""
    print("Installing POS Monitor Service...")
    
    # Set service recovery options
    import subprocess
    
    try:
        # Install the service
        win32serviceutil.InstallService(
            POSMonitorService,
            POSMonitorService._svc_name_,
            POSMonitorService._svc_display_name_,
            startType=win32service.SERVICE_AUTO_START
        )
        
        # Set service description
        win32serviceutil.SetServiceCustomOption(
            POSMonitorService._svc_name_,
            "Description",
            POSMonitorService._svc_description_
        )
        
        print(f"Service '{POSMonitorService._svc_display_name_}' installed successfully")
        
        # Configure recovery options using sc command
        service_name = POSMonitorService._svc_name_
        
        # Set to restart on failure
        recovery_commands = [
            f'sc failure "{service_name}" reset=86400 actions=restart/60000/restart/60000/restart/60000',
            f'sc failureflag "{service_name}" 1'
        ]
        
        for cmd in recovery_commands:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✓ Configured: {cmd.split()[1]} {cmd.split()[2]}")
            else:
                print(f"✗ Failed: {cmd}")
                print(f"  Error: {result.stderr}")
        
        print("\nService installation complete!")
        print("You can start the service with: net start POSMonitor")
        
    except Exception as e:
        print(f"Error installing service: {e}")
        sys.exit(1)


def uninstall_service():
    """Uninstall the Windows service"""
    print("Uninstalling POS Monitor Service...")
    
    try:
        # Stop the service if running
        try:
            win32serviceutil.StopService(POSMonitorService._svc_name_)
            print("Service stopped")
        except:
            pass  # Service might not be running
        
        # Remove the service
        win32serviceutil.RemoveService(POSMonitorService._svc_name_)
        print(f"Service '{POSMonitorService._svc_display_name_}' uninstalled successfully")
        
    except Exception as e:
        print(f"Error uninstalling service: {e}")
        sys.exit(1)


def main():
    """Main entry point for service management"""
    if len(sys.argv) == 1:
        # Running as a service
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(POSMonitorService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # Command line arguments
        if sys.argv[1] == 'install':
            install_service()
        elif sys.argv[1] == 'remove' or sys.argv[1] == 'uninstall':
            uninstall_service()
        else:
            # Use standard service utilities
            win32serviceutil.HandleCommandLine(POSMonitorService)


if __name__ == '__main__':
    main()