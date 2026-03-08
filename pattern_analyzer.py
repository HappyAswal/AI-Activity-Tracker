"""
Pattern analysis and predictions using time series analysis.
"""

import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

DB_PATH = Path("activity.db")

class PatternAnalyzer:
    """Analyzes activity patterns and makes predictions."""
    
    def __init__(self):
        self.db_path = DB_PATH
    
    def get_activity_dataframe(self, days=7):
        """Load activity data into a pandas DataFrame."""
        if not self.db_path.exists():
            return pd.DataFrame()
        
        conn = sqlite3.connect(self.db_path)
        
        # Get data from last N days
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        query = """
            SELECT timestamp, app_name, window_title, category, is_idle
            FROM activity_log
            WHERE timestamp >= ?
            ORDER BY timestamp
        """
        
        df = pd.read_sql_query(query, conn, params=(cutoff_date,))
        conn.close()
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['date'] = df['timestamp'].dt.date
        
        return df
    
    def calculate_focus_score(self, df=None):
        """
        Calculate a focus score (0-100) based on recent activity.
        
        Returns:
            dict: Focus metrics
        """
        if df is None:
            df = self.get_activity_dataframe(days=1)
        
        if df.empty:
            return {
                'score': 0,
                'productivity_percentage': 0,
                'distraction_percentage': 0,
                'total_activities': 0
            }
        
        total = len(df)
        productive = len(df[df['category'] == 'Productivity'])
        distracted = len(df[df['category'].isin(['Entertainment', 'Social Media'])])
        idle = len(df[df['is_idle'] == 1])
        
        # Calculate score (0-100)
        active_time = total - idle
        if active_time > 0:
            productivity_ratio = productive / active_time
            distraction_ratio = distracted / active_time
            score = max(0, min(100, productivity_ratio * 100 - distraction_ratio * 50))
        else:
            score = 0
        
        return {
            'score': round(score, 1),
            'productivity_percentage': round((productive / total * 100) if total > 0 else 0, 1),
            'distraction_percentage': round((distracted / total * 100) if total > 0 else 0, 1),
            'total_activities': total
        }
    
    def get_peak_hours(self, df=None):
        """
        Identify peak productivity hours.
        
        Returns:
            list: Hours (0-23) sorted by productivity
        """
        if df is None:
            df = self.get_activity_dataframe(days=7)
        
        if df.empty:
            return []
        
        # Filter productive activities
        productive_df = df[df['category'] == 'Productivity']
        
        if productive_df.empty:
            return []
        
        # Count by hour
        hour_counts = productive_df['hour'].value_counts().sort_index()
        
        # Get top 3 hours
        top_hours = hour_counts.nlargest(3).index.tolist()
        
        return top_hours
    
    def detect_distraction_patterns(self, df=None):
        """
        Detect when user is most likely to get distracted.
        
        Returns:
            dict: Distraction patterns by hour and day
        """
        if df is None:
            df = self.get_activity_dataframe(days=7)
        
        if df.empty:
            return {'by_hour': {}, 'by_day': {}}
        
        # Filter distraction activities
        distracted_df = df[df['category'].isin(['Entertainment', 'Social Media'])]
        
        if distracted_df.empty:
            return {'by_hour': {}, 'by_day': {}}
        
        # Count by hour
        by_hour = distracted_df['hour'].value_counts().to_dict()
        
        # Count by day of week
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        by_day_counts = distracted_df['day_of_week'].value_counts().to_dict()
        by_day = {day_names[k]: v for k, v in by_day_counts.items()}
        
        return {
            'by_hour': by_hour,
            'by_day': by_day
        }
    
    def predict_next_hour_focus(self, df=None):
        """
        Predict focus level for the next hour based on patterns.
        
        Returns:
            str: Prediction (High, Medium, Low)
        """
        if df is None:
            df = self.get_activity_dataframe(days=7)
        
        if df.empty:
            return "Unknown"
        
        current_hour = datetime.now().hour
        next_hour = (current_hour + 1) % 24
        
        # Get historical data for this hour
        hour_data = df[df['hour'] == next_hour]
        
        if hour_data.empty:
            return "Unknown"
        
        # Calculate productivity ratio for this hour
        productive = len(hour_data[hour_data['category'] == 'Productivity'])
        total = len(hour_data[hour_data['is_idle'] == 0])
        
        if total == 0:
            return "Unknown"
        
        ratio = productive / total
        
        if ratio > 0.6:
            return "High"
        elif ratio > 0.3:
            return "Medium"
        else:
            return "Low"
    
    def get_daily_summary_stats(self):
        """
        Get comprehensive daily statistics.
        
        Returns:
            dict: Daily statistics
        """
        df = self.get_activity_dataframe(days=1)
        
        if df.empty:
            return None
        
        focus_score = self.calculate_focus_score(df)
        peak_hours = self.get_peak_hours(df)
        
        return {
            'focus_score': focus_score,
            'peak_hours': peak_hours,
            'total_apps_used': df['app_name'].nunique(),
            'most_used_app': df['app_name'].mode()[0] if not df.empty else "None"
        }

# Global instance
_pattern_analyzer = None

def get_pattern_analyzer():
    """Get or create the global pattern analyzer instance."""
    global _pattern_analyzer
    if _pattern_analyzer is None:
        _pattern_analyzer = PatternAnalyzer()
    return _pattern_analyzer
