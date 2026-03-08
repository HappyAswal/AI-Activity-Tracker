import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path("activity.db")

def init_database():
    """Initialize the SQLite database with required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            app_name TEXT NOT NULL,
            window_title TEXT,
            category TEXT,
            is_idle BOOLEAN DEFAULT 0
        )
    """)
    
    conn.commit()
    conn.close()

def log_activity(app_name, window_title, category, is_idle=False):
    """Insert a new activity log entry."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO activity_log (timestamp, app_name, window_title, category, is_idle)
        VALUES (?, ?, ?, ?, ?)
    """, (timestamp, app_name, window_title, category, is_idle))
    
    conn.commit()
    conn.close()

def get_recent_activity(minutes=15):
    """Retrieve activity logs from the last N minutes."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT timestamp, app_name, window_title, category, is_idle
        FROM activity_log
        WHERE datetime(timestamp) >= datetime('now', 'localtime', '-' || ? || ' minutes')
        ORDER BY timestamp DESC
    """, (minutes,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return rows
