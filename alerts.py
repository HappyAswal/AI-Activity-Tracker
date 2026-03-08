"""
Alert Manager - Monitors activity patterns and sends smart notifications.
"""

import time
from datetime import datetime, timedelta
from threading import Thread
from plyer import notification
from database import get_recent_activity

# Global flag to pause tracker
pause_tracking_until = None

def is_tracking_paused():
    global pause_tracking_until
    if pause_tracking_until and datetime.now() < pause_tracking_until:
        return True
    return False

# Alert thresholds (in minutes)
DISTRACTION_THRESHOLD = 15  # Alert after 15 minutes of distraction
PRODUCTIVITY_THRESHOLD = 90  # Alert for break after 90 minutes of work
CHECK_INTERVAL = 60  # Check every minute

# Categories considered as distractions
DISTRACTION_CATEGORIES = ['Entertainment', 'Social Media']

# Categories considered as productive
PRODUCTIVITY_CATEGORIES = ['Productivity']

class AlertManager:
    """Manages distraction and break alerts."""
    
    def __init__(self):
        self.last_distraction_alert = None
        self.last_break_alert = None
        self.alert_cooldown = timedelta(minutes=30)  # Don't spam alerts
    
    def can_send_alert(self, last_alert_time):
        """Check if enough time has passed since last alert."""
        if last_alert_time is None:
            return True
        return datetime.now() - last_alert_time > self.alert_cooldown
    
    def send_notification(self, title, message, timeout=10):
        """Send a native OS notification."""
        try:
            notification.notify(
                title=title,
                message=message,
                app_name='AI Activity Tracker',
                timeout=timeout
            )
            print(f"[ALERT] {title}: {message}")
        except Exception as e:
            print(f"[ERROR] Failed to send notification: {e}")
    
    def check_distraction_pattern(self):
        """Check if user has been distracted for 15+ minutes straight."""
        recent = get_recent_activity(minutes=DISTRACTION_THRESHOLD)
        
        if not recent:
            return
            
        # Check if we have enough data to consider it continuous (margin of 1 poll interval = 5 seconds)
        oldest_time = datetime.fromisoformat(recent[-1][0])
        if (datetime.now() - oldest_time).total_seconds() < (DISTRACTION_THRESHOLD * 60) - 5:
            return  # Not enough continuous data
        
        distraction_count = 0
        total_active = 0
        for entry in recent:
            timestamp, app_name, window_title, category, is_idle = entry
            
            if is_idle:
                continue  # Skip idle time
                
            total_active += 1
            if category in DISTRACTION_CATEGORIES:
                distraction_count += 1
        
        if total_active == 0:
            return
            
        # Trigger distraction alert if >= 90% distraction
        if (distraction_count / total_active) >= 0.90 and self.can_send_alert(self.last_distraction_alert):
            # Record the alert time
            self.last_distraction_alert = datetime.now()
            
            # Show interactive dialog
            self.show_distraction_dialog()
            
    def show_distraction_dialog(self):
        """Show an interactive OS dialog warning them about distraction."""
        import tkinter as tk
        from tkinter import messagebox
        
        # Create a hidden root window
        root = tk.Tk()
        root.withdraw()
        
        # Force window to top
        root.attributes('-topmost', True)
        
        # Ask the question
        messagebox.showwarning(
            "⚠️ Distraction Alert",
            f"You've been distracted for {DISTRACTION_THRESHOLD} minutes straight.\n\nTime to refocus! 🎯",
            parent=root
        )
            
        root.destroy()
    
    def check_productivity_pattern(self):
        """Check if user has been productive for 90 minutes straight."""
        global pause_tracking_until
        recent = get_recent_activity(minutes=PRODUCTIVITY_THRESHOLD)
        
        if not recent:
            return
            
        # Check if we have enough data to consider it continuous (margin of 1 poll interval = 5 seconds)
        oldest_time = datetime.fromisoformat(recent[-1][0])
        if (datetime.now() - oldest_time).total_seconds() < (PRODUCTIVITY_THRESHOLD * 60) - 5:
            return  # Not enough continuous data
        
        productivity_count = 0
        total_active = 0
        for entry in recent:
            timestamp, app_name, window_title, category, is_idle = entry
            
            if is_idle:
                continue  # Skip idle time
                
            total_active += 1
            if category in PRODUCTIVITY_CATEGORIES:
                productivity_count += 1
            elif category in DISTRACTION_CATEGORIES:
                return # Gap found! They played a game or watched a video. Not straight productivity.
        
        if total_active == 0:
            return
            
        # Trigger break alert if mostly productive
        if (productivity_count / total_active) > 0.90 and self.can_send_alert(self.last_break_alert):
            
            # Record the alert time so we don't spam them, regardless of their choice
            self.last_break_alert = datetime.now()
            
            # Show interactive dialog
            self.ask_break_dialog()
            
    def ask_break_dialog(self):
        """Show an interactive OS dialog asking if they want a 10 min break."""
        global pause_tracking_until
        import tkinter as tk
        from tkinter import messagebox
        
        # Create a hidden root window
        root = tk.Tk()
        root.withdraw()
        
        # Force window to top
        root.attributes('-topmost', True)
        
        # Ask the question
        take_break = messagebox.askyesno(
            "✨ Great Work!",
            f"You've been focused for {PRODUCTIVITY_THRESHOLD} mins straight.\n\nWould you like to take a 10 min break?\n(The tracker will pause if you click Yes)",
            parent=root
        )
        
        if take_break:
            pause_tracking_until = datetime.now() + timedelta(minutes=10)
            self.send_notification("Break Time", "Tracker paused for 10 minutes. Enjoy!")
        else:
            self.send_notification("Keep Going!", "Tracker is still active. Stay focused!")
            
        root.destroy()
    
    def run(self):
        """Main alert monitoring loop."""
        print("Alert Manager started.")
        print(f"Checking patterns every {CHECK_INTERVAL} seconds...")
        print(f"Distraction threshold: {DISTRACTION_THRESHOLD} minutes")
        print(f"Break reminder threshold: {PRODUCTIVITY_THRESHOLD} minutes\n")
        
        try:
            while True:
                self.check_distraction_pattern()
                self.check_productivity_pattern()
                time.sleep(CHECK_INTERVAL)
        except KeyboardInterrupt:
            print("\nAlert Manager stopped.")

def start_alert_manager():
    """Start the alert manager in a separate thread."""
    manager = AlertManager()
    thread = Thread(target=manager.run, daemon=True)
    thread.start()
    return thread

if __name__ == "__main__":
    # Run standalone for testing
    manager = AlertManager()
    manager.run()
