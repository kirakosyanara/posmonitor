"""
POS Application Hang Detection Module
Detects UI unresponsiveness in Windows applications using SendMessageTimeout
"""

import ctypes
import ctypes.wintypes
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
import time

# Windows constants
WM_NULL = 0x0000
SMTO_NORMAL = 0x0000
SMTO_BLOCK = 0x0001
SMTO_ABORTIFHUNG = 0x0002
SMTO_NOTIMEOUTIFNOTHUNG = 0x0008


class HangDetector:
    """Detects application UI hangs using Windows messaging"""
    
    def __init__(self, timeout_seconds: int = 5):
        """
        Initialize hang detector
        
        Args:
            timeout_seconds: Timeout in seconds to determine if app is hung
        """
        self.timeout_seconds = timeout_seconds
        self.timeout_ms = timeout_seconds * 1000
        self.logger = logging.getLogger("POSMonitor.HangDetector")
        
        # Windows API functions
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        
        # Track hang state
        self.last_hang_state: Dict[int, bool] = {}  # pid -> is_hung
        self.hang_start_time: Dict[int, datetime] = {}  # pid -> hang start time
        
    def find_windows_by_pid(self, pid: int) -> List[int]:
        """Find all top-level windows belonging to a process"""
        windows = []
        
        # Callback function for EnumWindows
        def enum_windows_callback(hwnd, lparam):
            # Get the process ID for this window
            window_pid = ctypes.wintypes.DWORD()
            self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
            
            # Check if it matches our target PID
            if window_pid.value == pid:
                # Only include visible top-level windows
                if self.user32.IsWindowVisible(hwnd) and not self.user32.GetParent(hwnd):
                    windows.append(hwnd)
            
            return True  # Continue enumeration
        
        # Define callback type
        WNDENUMPROC = ctypes.WINFUNCTYPE(
            ctypes.wintypes.BOOL,
            ctypes.wintypes.HWND,
            ctypes.wintypes.LPARAM
        )
        
        # Convert Python function to C callback
        callback = WNDENUMPROC(enum_windows_callback)
        
        # Enumerate all windows
        self.user32.EnumWindows(callback, 0)
        
        return windows
    
    def get_window_title(self, hwnd: int) -> str:
        """Get the title of a window"""
        length = self.user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return ""
        
        buffer = ctypes.create_unicode_buffer(length + 1)
        self.user32.GetWindowTextW(hwnd, buffer, length + 1)
        return buffer.value
    
    def is_window_responsive(self, hwnd: int) -> bool:
        """Check if a window is responsive using SendMessageTimeout"""
        result = ctypes.wintypes.DWORD()
        
        # Send WM_NULL message with timeout
        ret = self.user32.SendMessageTimeoutW(
            hwnd,                    # Window handle
            WM_NULL,                 # Message (WM_NULL is a no-op)
            0,                       # wParam
            0,                       # lParam
            SMTO_ABORTIFHUNG,       # Flags
            self.timeout_ms,         # Timeout in milliseconds
            ctypes.byref(result)     # Result
        )
        
        # If SendMessageTimeout returns 0, the window is not responding
        return ret != 0
    
    def check_process_responsiveness(self, pid: int, process_name: str) -> Optional[Dict[str, Any]]:
        """
        Check if a process's UI is responsive
        
        Returns:
            None if responsive, hang info dict if hung
        """
        try:
            # Find windows for this process
            windows = self.find_windows_by_pid(pid)
            
            if not windows:
                # No windows found - might be a background process
                self.logger.debug(f"No windows found for process {process_name} (PID: {pid})")
                # Clear any previous hang state
                if pid in self.last_hang_state:
                    del self.last_hang_state[pid]
                    del self.hang_start_time[pid]
                return None
            
            # Check each window
            hung_windows = []
            for hwnd in windows:
                title = self.get_window_title(hwnd)
                if not self.is_window_responsive(hwnd):
                    hung_windows.append({
                        "hwnd": hwnd,
                        "title": title
                    })
                    self.logger.warning(f"Window not responding: '{title}' (HWND: {hwnd})")
            
            # Determine overall hang state
            is_hung = len(hung_windows) > 0
            was_hung = self.last_hang_state.get(pid, False)
            
            if is_hung and not was_hung:
                # Just started hanging
                self.hang_start_time[pid] = datetime.now(timezone.utc)
                self.last_hang_state[pid] = True
                
                return {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "type": "hang",
                    "process_name": process_name,
                    "pid": pid,
                    "duration_seconds": 0,
                    "window_count": len(windows),
                    "hung_windows": hung_windows,
                    "recovered": False
                }
                
            elif is_hung and was_hung:
                # Still hanging - update duration
                duration = (datetime.now(timezone.utc) - self.hang_start_time[pid]).total_seconds()
                
                return {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "type": "hang_update",
                    "process_name": process_name,
                    "pid": pid,
                    "duration_seconds": round(duration, 1),
                    "window_count": len(windows),
                    "hung_windows": hung_windows,
                    "recovered": False
                }
                
            elif not is_hung and was_hung:
                # Recovered from hang
                duration = (datetime.now(timezone.utc) - self.hang_start_time[pid]).total_seconds()
                self.last_hang_state[pid] = False
                del self.hang_start_time[pid]
                
                return {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "type": "hang_recovery",
                    "process_name": process_name,
                    "pid": pid,
                    "duration_seconds": round(duration, 1),
                    "window_count": len(windows),
                    "recovered": True
                }
            
            # Not hung
            return None
            
        except Exception as e:
            self.logger.error(f"Error checking process responsiveness: {e}")
            return None
    
    def find_javafx_windows(self, pid: int) -> List[Dict[str, Any]]:
        """
        Find JavaFX-specific windows for a process
        JavaFX windows often have specific class names or properties
        """
        windows = []
        
        def enum_windows_callback(hwnd, lparam):
            window_pid = ctypes.wintypes.DWORD()
            self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(window_pid))
            
            if window_pid.value == pid:
                # Get window class name
                class_name = ctypes.create_unicode_buffer(256)
                self.user32.GetClassNameW(hwnd, class_name, 256)
                
                # JavaFX windows often have class names like "GlassWndClass"
                # or contain "JavaFX" in the title
                title = self.get_window_title(hwnd)
                
                if "glass" in class_name.value.lower() or "javafx" in title.lower():
                    windows.append({
                        "hwnd": hwnd,
                        "title": title,
                        "class_name": class_name.value
                    })
                    self.logger.debug(f"Found JavaFX window: {title} (Class: {class_name.value})")
            
            return True
        
        WNDENUMPROC = ctypes.WINFUNCTYPE(
            ctypes.wintypes.BOOL,
            ctypes.wintypes.HWND,
            ctypes.wintypes.LPARAM
        )
        
        callback = WNDENUMPROC(enum_windows_callback)
        self.user32.EnumWindows(callback, 0)
        
        return windows


def test_hang_detector():
    """Test the hang detector with a sample application"""
    import subprocess
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    detector = HangDetector(timeout_seconds=3)
    
    print("Hang Detector Test")
    print("=" * 50)
    
    # Test with notepad
    print("Starting notepad for testing...")
    proc = subprocess.Popen(["notepad.exe"])
    time.sleep(2)  # Let it start
    
    print(f"Testing responsiveness of notepad (PID: {proc.pid})...")
    
    # Test several times
    for i in range(5):
        result = detector.check_process_responsiveness(proc.pid, "notepad.exe")
        if result:
            print(f"Hang detected: {result}")
        else:
            print(f"Process is responsive (check {i+1}/5)")
        time.sleep(2)
    
    # Find JavaFX windows (won't find any for notepad, but demonstrates the API)
    javafx_windows = detector.find_javafx_windows(proc.pid)
    print(f"\nJavaFX windows found: {len(javafx_windows)}")
    
    proc.terminate()
    print("\nTest completed!")


if __name__ == "__main__":
    test_hang_detector()