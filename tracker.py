"""
Main tracker daemon that monitors active applications and logs activity.
"""

import time
import psutil
from datetime import datetime
from pynput import mouse, keyboard
from threading import Thread, Lock

try:
    import pygetwindow as gw
except ImportError:
    gw = None

from database import init_database, log_activity
from categorizer import categorize_activity, DataCleaner
from alerts import start_alert_manager, is_tracking_paused

# Try to use two-stage ML categorizer if available
try:
    from ml_categorizer import categorize_with_ml
    USE_ML = True
    print("Two-stage ML categorizer loaded. Using AI-powered categorization.")
    print("  Stage 1: TF-IDF + Logistic Regression")
    print("  Stage 2: TF-IDF + SVM (for video content)")
except ImportError:
    USE_ML = False
    print("ML libraries not installed. Using rule-based categorization.")

# Idle detection settings
IDLE_THRESHOLD_SECONDS = 120  # 2 minutes
POLL_INTERVAL_SECONDS = 5

class IdleDetector:
    """Tracks user input activity to detect idle state."""
    
    def __init__(self):
        self.last_activity_time = time.time()
        self.lock = Lock()
        
    def on_activity(self):
        """Called when user input is detected."""
        with self.lock:
            self.last_activity_time = time.time()
    
    def is_idle(self):
        """Check if user has been idle for longer than threshold."""
        with self.lock:
            return (time.time() - self.last_activity_time) > IDLE_THRESHOLD_SECONDS
    
    def start_monitoring(self):
        """Start listening to mouse and keyboard events."""
        def on_move(x, y):
            self.on_activity()
        
        def on_click(x, y, button, pressed):
            self.on_activity()
        
        def on_scroll(x, y, dx, dy):
            self.on_activity()
        
        def on_press(key):
            self.on_activity()
        
        # Start mouse listener
        mouse_listener = mouse.Listener(
            on_move=on_move,
            on_click=on_click,
            on_scroll=on_scroll
        )
        mouse_listener.daemon = True
        mouse_listener.start()
        
        # Start keyboard listener
        keyboard_listener = keyboard.Listener(on_press=on_press)
        keyboard_listener.daemon = True
        keyboard_listener.start()

def get_active_window():
    """Get the currently active window information."""
    if gw is None:
        return "Unknown", "pygetwindow not available"
    
    try:
        active_window = gw.getActiveWindow()
        if active_window:
            return active_window.title, active_window.title
        return "Unknown", "No active window"
    except Exception as e:
        return "Unknown", str(e)

def get_active_process():
    """Get the name of the active process."""
    try:
        # Get foreground window process (Windows-specific approach)
        import ctypes
        user32 = ctypes.windll.user32
        h_wnd = user32.GetForegroundWindow()
        
        if h_wnd:
            pid = ctypes.c_ulong()
            user32.GetWindowThreadProcessId(h_wnd, ctypes.byref(pid))
            
            try:
                process = psutil.Process(pid.value)
                return process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return "Unknown"
    except Exception:
        return "Unknown"

def main():
    """Main tracker loop."""
    print("Initializing AI Activity Tracker...")
    
    # Initialize database
    init_database()
    print("Database initialized.")
    
    # Start idle detection
    idle_detector = IdleDetector()
    idle_detector.start_monitoring()
    print("Idle detection started.")
    
    # Start alert manager
    start_alert_manager()
    print("Alert manager started.")
    
    print(f"Tracker running. Polling every {POLL_INTERVAL_SECONDS} seconds...")
    print("Press Ctrl+C to stop.\n")
    
    try:
        while True:
            # Check if tracker is paused due to a break
            if is_tracking_paused():
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"[{timestamp}] PAUSED | Enjoy your break! Tracker sleeping...")
                time.sleep(POLL_INTERVAL_SECONDS)
                continue
                
            # Get current window and process info
            raw_title, _ = get_active_window()
            raw_app = get_active_process()
            
            # Prevent Tkinter alert pop-ups from breaking the continuous tracking streaks
            if raw_title in ["⚠️ Distraction Alert", "✨ Great Work!"]:
                time.sleep(POLL_INTERVAL_SECONDS)
                continue
            
            # Check if user is idle
            is_idle = idle_detector.is_idle()
            
            # Pre-process Data immediately so the database only ever stores perfectly clean tags
            app_name, window_title = DataCleaner.clean(raw_app, raw_title)
            
            # Categorize the activity (use ML if available)
            if USE_ML:
                category = categorize_with_ml(app_name, window_title)
            else:
                category = categorize_activity(app_name, window_title)
            
            # Log to database
            log_activity(app_name, window_title, category, is_idle)
            
            # Console output for monitoring
            status = "IDLE" if is_idle else "ACTIVE"
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] {status} | {category:15} | {app_name:20} | {window_title[:50]}")
            
            # Wait before next poll
            time.sleep(POLL_INTERVAL_SECONDS)
            
    except KeyboardInterrupt:
        print("\n\nTracker stopped by user.")

if __name__ == "__main__":
    main()
