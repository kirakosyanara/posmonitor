"""
Unit tests for POS Monitor components
"""

import unittest
import tempfile
import json
import time
import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import psutil
from pos_monitor_core import POSMonitor
from pos_monitor_async_logger import AsyncLogger

# Only import Windows-specific modules if on Windows
if sys.platform == "win32":
    from pos_monitor_hang_detector import HangDetector
    from pos_monitor_event_log import EventLogMonitor


class TestAsyncLogger(unittest.TestCase):
    """Test cases for AsyncLogger"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "max_file_size_mb": 1,
            "retention_days": 7,
            "batch_size": 5,
            "flush_interval": 1
        }
        self.logger = AsyncLogger(self.temp_dir, self.config)
        self.logger.start()
    
    def tearDown(self):
        """Clean up test environment"""
        self.logger.stop()
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_basic_logging(self):
        """Test basic log entry writing"""
        # Write test entries
        for i in range(10):
            entry = {
                "type": "test",
                "sequence": i,
                "data": f"Test message {i}"
            }
            success = self.logger.write_entry(entry)
            self.assertTrue(success, f"Failed to write entry {i}")
        
        # Wait for flush
        time.sleep(2)
        
        # Check if entries were written
        log_files = list(Path(self.temp_dir).glob("pos_monitor_*.json"))
        self.assertGreater(len(log_files), 0, "No log files created")
        
        # Read and verify entries
        entries = []
        for log_file in log_files:
            with open(log_file, 'r') as f:
                for line in f:
                    entries.append(json.loads(line))
        
        self.assertEqual(len(entries), 10, "Not all entries were written")
        
        # Verify sequence
        for i, entry in enumerate(entries):
            self.assertEqual(entry["sequence"], i)
    
    def test_file_rotation(self):
        """Test log file rotation by size"""
        # Write large entries to trigger rotation
        large_data = "x" * 10000  # 10KB per entry
        
        for i in range(150):  # Should trigger rotation
            entry = {
                "type": "large",
                "sequence": i,
                "data": large_data
            }
            self.logger.write_entry(entry)
        
        # Wait for flush and rotation
        time.sleep(3)
        
        # Check for rotated files
        log_files = list(Path(self.temp_dir).glob("pos_monitor_*.json*"))
        rotated_files = [f for f in log_files if ".1.json" in f.name or ".json.gz" in f.name]
        
        self.assertGreater(len(rotated_files), 0, "No rotated files found")
    
    def test_stats_tracking(self):
        """Test statistics tracking"""
        # Write some entries
        for i in range(20):
            self.logger.write_entry({"test": i})
        
        time.sleep(2)
        
        # Get stats
        stats = self.logger.get_stats()
        
        self.assertIn("entries_written", stats)
        self.assertIn("files_rotated", stats)
        self.assertIn("queue_size", stats)
        self.assertGreater(stats["entries_written"], 0)


class TestCrashDetection(unittest.TestCase):
    """Test cases for crash detection functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "log_dir": self.temp_dir,
            "performance_interval": 60,
            "process_check_interval": 5
        }
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_exit_code_interpretation(self):
        """Test exit code interpretation"""
        monitor = POSMonitor("test.exe", self.config)
        
        # Test known exit codes
        test_cases = [
            (0, "normal", "Normal termination"),
            (-1073741819, "crash", "Access violation"),
            (-1073741571, "crash", "Stack overflow"),
            (-805306369, "crash", "Java OutOfMemoryError"),
            (1, "error", "General error"),
            (100, "error", "Process exited with code 100")
        ]
        
        for exit_code, expected_type, expected_desc in test_cases:
            result = monitor.interpret_exit_code(exit_code)
            self.assertEqual(result["type"], expected_type)
            self.assertIn(expected_desc, result["description"])
    
    def test_crash_context_collection(self):
        """Test crash context collection"""
        monitor = POSMonitor("test.exe", self.config)
        
        # Mock a process
        mock_process = Mock()
        mock_process.cpu_percent.return_value = 50.0
        mock_process.memory_info.return_value = Mock(rss=100*1024*1024, vms=200*1024*1024)
        mock_process.memory_percent.return_value = 10.0
        mock_process.num_threads.return_value = 5
        mock_process.create_time.return_value = time.time() - 3600  # 1 hour ago
        mock_process.is_running.return_value = True
        
        monitor.target_process = mock_process
        
        # Get crash context
        context = monitor.get_crash_context()
        
        self.assertIn("last_metrics", context)
        self.assertIn("uptime_seconds", context)
        self.assertIn("create_time", context)
        self.assertAlmostEqual(context["uptime_seconds"], 3600, delta=10)


@unittest.skipUnless(sys.platform == "win32", "Windows-specific tests")
class TestHangDetector(unittest.TestCase):
    """Test cases for hang detector (Windows only)"""
    
    def setUp(self):
        """Set up test environment"""
        self.detector = HangDetector(timeout_seconds=2)
    
    def test_window_discovery(self):
        """Test window discovery functionality"""
        # This test requires a running process with windows
        # We'll test the method exists and returns a list
        windows = self.detector.find_windows_by_pid(os.getpid())
        self.assertIsInstance(windows, list)
    
    def test_responsiveness_check(self):
        """Test responsiveness checking"""
        # Mock window handle
        mock_hwnd = 0x12345
        
        # We can't easily test the actual Windows API call,
        # but we can verify the method exists and handles invalid windows
        result = self.detector.is_window_responsive(mock_hwnd)
        self.assertIsInstance(result, bool)


@unittest.skipUnless(sys.platform == "win32", "Windows-specific tests")
class TestEventLogMonitor(unittest.TestCase):
    """Test cases for event log monitor (Windows only)"""
    
    def setUp(self):
        """Set up test environment"""
        self.config = {
            "sources": ["Application"],
            "levels": ["Error", "Warning"],
            "java_keywords": ["java", "exception"]
        }
        self.monitor = EventLogMonitor("test.exe", self.config)
    
    def test_event_relevance_check(self):
        """Test event relevance checking"""
        # Test relevant event (contains process name)
        event_dict = {
            "Message": "Error in test.exe application",
            "StringInserts": ["test.exe", "crashed"]
        }
        self.assertTrue(self.monitor._is_relevant_event(event_dict))
        
        # Test relevant event (contains Java keyword)
        event_dict = {
            "Message": "java.lang.OutOfMemoryError occurred",
            "StringInserts": []
        }
        self.assertTrue(self.monitor._is_relevant_event(event_dict))
        
        # Test irrelevant event
        event_dict = {
            "Message": "Some other application error",
            "StringInserts": ["other.exe"]
        }
        self.assertFalse(self.monitor._is_relevant_event(event_dict))
    
    def test_java_error_parsing(self):
        """Test Java error parsing"""
        # Test exception parsing
        message = "java.lang.NullPointerException: Cannot invoke method on null\n\tat com.example.Class.method(Class.java:42)"
        result = self.monitor._parse_java_error(message)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["exception_type"], "NullPointerException")
        self.assertIn("stack_trace", result)
        
        # Test OutOfMemoryError parsing
        message = "java.lang.OutOfMemoryError: Java heap space"
        result = self.monitor._parse_java_error(message)
        
        self.assertIsNotNone(result)
        self.assertEqual(result["memory_area"], "Java heap space")


class TestResourceMonitoring(unittest.TestCase):
    """Test cases for resource monitoring"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "log_dir": self.temp_dir,
            "monitor_self": True,
            "self_monitor_interval": 1,
            "max_memory_mb": 100,
            "max_cpu_percent": 50
        }
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('psutil.Process')
    def test_self_monitoring(self, mock_process_class):
        """Test self resource monitoring"""
        # Mock process metrics
        mock_process = Mock()
        mock_process.cpu_percent.return_value = 2.5
        mock_process.memory_info.return_value = Mock(rss=30*1024*1024)
        mock_process.num_threads.return_value = 10
        mock_process_class.return_value = mock_process
        
        monitor = POSMonitor("test.exe", self.config)
        
        # Verify resource limits are set
        self.assertEqual(monitor.resource_limits["max_memory_mb"], 100)
        self.assertEqual(monitor.resource_limits["max_cpu_percent"], 50)
        
        # Verify self process is initialized
        self.assertIsNotNone(monitor.self_process)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete system"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.config = {
            "log_dir": self.temp_dir,
            "performance_interval": 1,
            "process_check_interval": 1,
            "logging": {
                "async_enabled": True,
                "max_file_size_mb": 10,
                "batch_size": 5
            }
        }
    
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('psutil.process_iter')
    @patch('psutil.Process')
    def test_full_monitoring_cycle(self, mock_process_class, mock_process_iter):
        """Test a full monitoring cycle"""
        # Mock process discovery
        mock_proc_info = {'pid': 1234, 'name': 'test.exe'}
        mock_process_iter.return_value = [Mock(info=mock_proc_info)]
        
        # Mock process metrics
        mock_process = Mock()
        mock_process.is_running.return_value = True
        mock_process.cpu_percent.return_value = 25.0
        mock_process.memory_info.return_value = Mock(rss=50*1024*1024, vms=100*1024*1024)
        mock_process.memory_percent.return_value = 5.0
        mock_process.num_threads.return_value = 8
        mock_process.pid = 1234
        mock_process_class.return_value = mock_process
        
        # Create monitor
        monitor = POSMonitor("test.exe", self.config)
        
        # Start monitoring in a thread
        import threading
        monitor_thread = threading.Thread(target=monitor.start)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        # Let it run for a few seconds
        time.sleep(3)
        
        # Stop monitor
        monitor.stop()
        
        # Wait for thread to finish
        monitor_thread.join(timeout=5)
        
        # Check if logs were created
        log_files = list(Path(self.temp_dir).glob("pos_monitor_*.json"))
        self.assertGreater(len(log_files), 0, "No log files created")
        
        # Read and verify log entries
        entries = []
        for log_file in log_files:
            with open(log_file, 'r') as f:
                for line in f:
                    entries.append(json.loads(line))
        
        # Check for different entry types
        entry_types = {entry["type"] for entry in entries}
        self.assertIn("process_started", entry_types)
        self.assertIn("performance", entry_types)
        self.assertIn("monitor_stopped", entry_types)


if __name__ == "__main__":
    # Run tests with verbosity
    unittest.main(verbosity=2)