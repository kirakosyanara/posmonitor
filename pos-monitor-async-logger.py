"""
Async Logging Queue Module
Provides thread-safe, high-performance logging with batching and error handling
"""

import json
import logging
import os
import queue
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List
import gzip
import shutil


class AsyncLogger:
    """Thread-safe async logger with batching and rotation"""
    
    def __init__(self, log_dir: str, config: Dict[str, Any]):
        """
        Initialize async logger
        
        Args:
            log_dir: Directory for log files
            config: Logging configuration
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.max_file_size_mb = config.get("max_file_size_mb", 100)
        self.max_file_size_bytes = self.max_file_size_mb * 1024 * 1024
        self.retention_days = config.get("retention_days", 30)
        self.batch_size = config.get("batch_size", 50)
        self.flush_interval = config.get("flush_interval", 5)  # seconds
        
        # Queue for log entries
        self.log_queue = queue.Queue(maxsize=10000)
        self.batch_buffer = []
        
        # Threading
        self.logger = logging.getLogger("POSMonitor.AsyncLogger")
        self.stop_event = threading.Event()
        self.worker_thread = None
        self.last_flush_time = time.time()
        
        # File handles
        self.current_file_handle = None
        self.current_file_path = None
        self.current_file_size = 0
        
        # Statistics
        self.stats = {
            "entries_written": 0,
            "entries_dropped": 0,
            "files_rotated": 0,
            "write_errors": 0
        }
        
    def start(self):
        """Start the async logger worker thread"""
        self.worker_thread = threading.Thread(
            target=self._worker_loop,
            name="AsyncLoggerWorker",
            daemon=True
        )
        self.worker_thread.start()
        self.logger.info("Async logger started")
        
        # Start cleanup thread
        cleanup_thread = threading.Thread(
            target=self._cleanup_old_logs,
            name="LogCleanupWorker",
            daemon=True
        )
        cleanup_thread.start()
    
    def stop(self):
        """Stop the async logger and flush remaining entries"""
        self.logger.info("Stopping async logger...")
        self.stop_event.set()
        
        # Flush remaining entries
        self._flush_batch(force=True)
        
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        
        # Close file handle
        if self.current_file_handle:
            self.current_file_handle.close()
        
        self.logger.info(f"Async logger stopped. Stats: {self.stats}")
    
    def write_entry(self, entry: Dict[str, Any]) -> bool:
        """
        Queue a log entry for writing
        
        Args:
            entry: Log entry to write
            
        Returns:
            True if queued successfully, False if queue is full
        """
        # Ensure timestamp
        if 'timestamp' not in entry:
            entry['timestamp'] = datetime.now(timezone.utc).isoformat()
        
        try:
            self.log_queue.put_nowait(entry)
            return True
        except queue.Full:
            self.stats["entries_dropped"] += 1
            self.logger.warning("Log queue full, dropping entry")
            return False
    
    def _worker_loop(self):
        """Main worker loop for processing log entries"""
        while not self.stop_event.is_set():
            try:
                # Get entries from queue with timeout
                try:
                    entry = self.log_queue.get(timeout=1)
                    self.batch_buffer.append(entry)
                    
                    # Check if we should flush
                    if (len(self.batch_buffer) >= self.batch_size or 
                        time.time() - self.last_flush_time >= self.flush_interval):
                        self._flush_batch()
                        
                except queue.Empty:
                    # No entries, check if we need to flush based on time
                    if (self.batch_buffer and 
                        time.time() - self.last_flush_time >= self.flush_interval):
                        self._flush_batch()
                    
            except Exception as e:
                self.logger.error(f"Error in logger worker loop: {e}")
                self.stats["write_errors"] += 1
    
    def _flush_batch(self, force: bool = False):
        """Flush the current batch to disk"""
        if not self.batch_buffer and not force:
            return
        
        try:
            # Get or create file handle
            file_handle = self._get_file_handle()
            if not file_handle:
                return
            
            # Write batch
            for entry in self.batch_buffer:
                json_line = json.dumps(entry, separators=(',', ':')) + '\n'
                file_handle.write(json_line)
                self.current_file_size += len(json_line.encode('utf-8'))
                self.stats["entries_written"] += 1
            
            # Flush to disk
            file_handle.flush()
            os.fsync(file_handle.fileno())
            
            # Clear batch
            self.batch_buffer.clear()
            self.last_flush_time = time.time()
            
            # Check if rotation needed
            if self.current_file_size >= self.max_file_size_bytes:
                self._rotate_log_file()
                
        except Exception as e:
            self.logger.error(f"Error flushing batch: {e}")
            self.stats["write_errors"] += 1
    
    def _get_file_handle(self):
        """Get or create the current log file handle"""
        today = datetime.now().strftime("%Y-%m-%d")
        expected_file_name = f"pos_monitor_{today}.json"
        expected_file_path = self.log_dir / expected_file_name
        
        # Check if we need a new file (new day or no file open)
        if (not self.current_file_handle or 
            self.current_file_path.name != expected_file_name):
            
            # Close existing handle
            if self.current_file_handle:
                self.current_file_handle.close()
            
            # Open new file
            try:
                self.current_file_handle = open(
                    expected_file_path, 'a', encoding='utf-8', buffering=8192
                )
                self.current_file_path = expected_file_path
                
                # Get current file size
                self.current_file_size = expected_file_path.stat().st_size
                
            except Exception as e:
                self.logger.error(f"Error opening log file: {e}")
                self.current_file_handle = None
                return None
        
        return self.current_file_handle
    
    def _rotate_log_file(self):
        """Rotate the current log file when it exceeds size limit"""
        if not self.current_file_handle:
            return
        
        try:
            # Close current file
            self.current_file_handle.close()
            self.current_file_handle = None
            
            # Generate rotation name with sequence number
            base_name = self.current_file_path.stem
            sequence = 1
            
            while True:
                rotated_name = f"{base_name}.{sequence}.json"
                rotated_path = self.current_file_path.parent / rotated_name
                
                if not rotated_path.exists():
                    break
                sequence += 1
            
            # Rename current file
            self.current_file_path.rename(rotated_path)
            
            # Compress rotated file
            self._compress_log_file(rotated_path)
            
            self.stats["files_rotated"] += 1
            self.logger.info(f"Rotated log file to {rotated_name}")
            
            # Reset file size counter
            self.current_file_size = 0
            
        except Exception as e:
            self.logger.error(f"Error rotating log file: {e}")
    
    def _compress_log_file(self, file_path: Path):
        """Compress a log file using gzip"""
        try:
            gz_path = file_path.with_suffix('.json.gz')
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(gz_path, 'wb', compresslevel=6) as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove original file
            file_path.unlink()
            
            self.logger.debug(f"Compressed log file: {gz_path.name}")
            
        except Exception as e:
            self.logger.error(f"Error compressing log file: {e}")
    
    def _cleanup_old_logs(self):
        """Clean up log files older than retention period"""
        while not self.stop_event.is_set():
            try:
                cutoff_time = time.time() - (self.retention_days * 24 * 60 * 60)
                
                # Find old files
                for file_path in self.log_dir.glob("pos_monitor_*.json*"):
                    try:
                        if file_path.stat().st_mtime < cutoff_time:
                            file_path.unlink()
                            self.logger.info(f"Deleted old log file: {file_path.name}")
                    except Exception as e:
                        self.logger.error(f"Error deleting old log: {e}")
                
                # Run cleanup once per hour
                self.stop_event.wait(3600)
                
            except Exception as e:
                self.logger.error(f"Error in cleanup thread: {e}")
                self.stop_event.wait(3600)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get logger statistics"""
        return {
            **self.stats,
            "queue_size": self.log_queue.qsize(),
            "batch_size": len(self.batch_buffer)
        }


def test_async_logger():
    """Test the async logger"""
    import random
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    config = {
        "max_file_size_mb": 1,  # Small size for testing
        "retention_days": 7,
        "batch_size": 10,
        "flush_interval": 2
    }
    
    logger = AsyncLogger("./test_logs", config)
    logger.start()
    
    print("Async Logger Test")
    print("=" * 50)
    
    # Generate test entries
    print("Generating test log entries...")
    
    for i in range(100):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "test",
            "sequence": i,
            "data": {
                "value": random.randint(1, 100),
                "message": f"Test message {i}"
            }
        }
        
        success = logger.write_entry(entry)
        if not success:
            print(f"Failed to write entry {i}")
        
        time.sleep(0.1)
    
    # Wait for flush
    print("\nWaiting for final flush...")
    time.sleep(3)
    
    # Get stats
    stats = logger.get_stats()
    print(f"\nLogger Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Stop logger
    logger.stop()
    print("\nTest completed!")


if __name__ == "__main__":
    test_async_logger()