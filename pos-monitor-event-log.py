"""
POS Application Event Log Monitor
Monitors Windows Event Logs for application errors and Java-specific issues
"""

import win32evtlog
import win32evtlogutil
import win32con
import pywintypes
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import re
import time


class EventLogMonitor:
    """Monitors Windows Event Logs for application-specific events"""
    
    def __init__(self, process_name: str, config: Dict[str, Any]):
        """
        Initialize event log monitor
        
        Args:
            process_name: Name of the process to monitor
            config: Event log configuration
        """
        self.process_name = process_name
        self.config = config
        self.logger = logging.getLogger("POSMonitor.EventLog")
        
        # Event sources to monitor
        self.sources = config.get("sources", ["Application", "System"])
        
        # Event levels to capture
        level_map = {
            "Error": win32evtlog.EVENTLOG_ERROR_TYPE,
            "Warning": win32evtlog.EVENTLOG_WARNING_TYPE,
            "Critical": win32evtlog.EVENTLOG_ERROR_TYPE  # Map critical to error
        }
        
        self.levels = []
        for level in config.get("levels", ["Error", "Warning", "Critical"]):
            if level in level_map:
                self.levels.append(level_map[level])
        
        # Java-specific keywords to look for
        self.java_keywords = config.get("java_keywords", [
            "java", "jvm", "javafx", "OutOfMemoryError", "StackOverflowError",
            "NullPointerException", "heap space"
        ])
        
        # Track last event record numbers to avoid duplicates
        self.last_record_numbers = {}
        
    def _is_relevant_event(self, event_dict: Dict[str, Any]) -> bool:
        """Check if an event is relevant to our monitored process"""
        # Check if event contains process name
        strings = event_dict.get("StringInserts", [])
        message = event_dict.get("Message", "")
        
        # Combine all text fields for searching
        all_text = message.lower()
        for s in strings:
            if s:
                all_text += " " + s.lower()
        
        # Check for process name
        if self.process_name.lower() in all_text:
            return True
        
        # Check for Java-specific keywords
        for keyword in self.java_keywords:
            if keyword.lower() in all_text:
                return True
        
        return False
    
    def _parse_java_error(self, message: str) -> Optional[Dict[str, Any]]:
        """Extract Java-specific error information from event message"""
        java_info = {}
        
        # Common Java exception patterns
        exception_pattern = r"(\w+(?:\.\w+)*Exception|Error)(?::?\s+(.+))?"
        match = re.search(exception_pattern, message)
        if match:
            java_info["exception_type"] = match.group(1)
            if match.group(2):
                java_info["exception_message"] = match.group(2).strip()
        
        # Look for stack trace
        if "\tat " in message:
            lines = message.split("\n")
            stack_lines = [line.strip() for line in lines if line.strip().startswith("at ")]
            if stack_lines:
                java_info["stack_trace"] = stack_lines[:10]  # First 10 lines
        
        # OutOfMemoryError details
        if "OutOfMemoryError" in message:
            heap_match = re.search(r"(Java heap space|Metaspace|Direct buffer memory)", message)
            if heap_match:
                java_info["memory_area"] = heap_match.group(1)
        
        return java_info if java_info else None
    
    def read_new_events(self, source: str) -> List[Dict[str, Any]]:
        """Read new events from a specific event log source"""
        events = []
        
        try:
            # Open the event log
            hand = win32evtlog.OpenEventLog(None, source)
            
            # Get total number of records
            total_records = win32evtlog.GetNumberOfEventLogRecords(hand)
            
            # Get last record number we processed
            last_record = self.last_record_numbers.get(source, 0)
            
            # Read events
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            
            # Read in batches
            batch_size = 100
            events_read = True
            
            while events_read:
                try:
                    event_batch = win32evtlog.ReadEventLog(hand, flags, 0)
                    
                    if not event_batch:
                        break
                    
                    for event in event_batch:
                        # Skip if we've already processed this record
                        if event.RecordNumber <= last_record:
                            continue
                        
                        # Check if event type matches our filter
                        if event.EventType not in self.levels:
                            continue
                        
                        # Convert to dictionary
                        event_dict = {
                            "RecordNumber": event.RecordNumber,
                            "TimeGenerated": event.TimeGenerated,
                            "EventID": event.EventID & 0xFFFF,  # Extract actual event ID
                            "EventType": event.EventType,
                            "SourceName": event.SourceName,
                            "ComputerName": event.ComputerName,
                            "StringInserts": event.StringInserts,
                            "EventCategory": event.EventCategory,
                        }
                        
                        # Get formatted message
                        try:
                            event_dict["Message"] = win32evtlogutil.SafeFormatMessage(event, source)
                        except:
                            event_dict["Message"] = "Unable to format message"
                        
                        # Check if relevant to our process
                        if self._is_relevant_event(event_dict):
                            # Parse Java-specific information
                            java_info = self._parse_java_error(event_dict["Message"])
                            if java_info:
                                event_dict["java_details"] = java_info
                            
                            events.append(event_dict)
                        
                        # Update last record number
                        self.last_record_numbers[source] = max(
                            self.last_record_numbers.get(source, 0),
                            event.RecordNumber
                        )
                    
                except pywintypes.error as e:
                    if e.winerror == 38:  # Reached end of log
                        break
                    else:
                        raise
            
            # Close the event log
            win32evtlog.CloseEventLog(hand)
            
        except Exception as e:
            self.logger.error(f"Error reading event log {source}: {e}")
        
        return events
    
    def format_event_log_entry(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Format event log entry for JSON logging"""
        # Map event types to readable names
        type_map = {
            win32evtlog.EVENTLOG_ERROR_TYPE: "Error",
            win32evtlog.EVENTLOG_WARNING_TYPE: "Warning",
            win32evtlog.EVENTLOG_INFORMATION_TYPE: "Information",
        }
        
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "event_log",
            "process_name": self.process_name,
            "source": event["SourceName"],
            "event_id": event["EventID"],
            "level": type_map.get(event["EventType"], "Unknown"),
            "message": event["Message"],
            "computer_name": event["ComputerName"],
            "time_generated": event["TimeGenerated"].isoformat() if event["TimeGenerated"] else None,
        }
        
        # Add Java details if present
        if "java_details" in event:
            log_entry["java_details"] = event["java_details"]
        
        return log_entry
    
    def check_event_logs(self) -> List[Dict[str, Any]]:
        """Check all configured event log sources for new events"""
        all_events = []
        
        for source in self.sources:
            self.logger.debug(f"Checking event log: {source}")
            events = self.read_new_events(source)
            
            if events:
                self.logger.info(f"Found {len(events)} relevant events in {source}")
                
                # Format events for logging
                for event in events:
                    formatted = self.format_event_log_entry(event)
                    all_events.append(formatted)
        
        return all_events


def test_event_log_monitor():
    """Test the event log monitor"""
    import json
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    config = {
        "sources": ["Application", "System"],
        "levels": ["Error", "Warning"],
        "java_keywords": ["java", "exception", "error"]
    }
    
    monitor = EventLogMonitor("notepad.exe", config)
    
    print("Event Log Monitor Test")
    print("=" * 50)
    print("Checking for recent application errors...")
    
    events = monitor.check_event_logs()
    
    if events:
        print(f"\nFound {len(events)} relevant events:")
        for event in events:
            print(f"\n{json.dumps(event, indent=2)}")
    else:
        print("\nNo relevant events found")
    
    print("\nTest completed!")


if __name__ == "__main__":
    test_event_log_monitor()