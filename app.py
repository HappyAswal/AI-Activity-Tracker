"""
FastAPI web server for the Activity Tracker Dashboard.
Provides REST API endpoints for activity statistics, insights, and ML model management.
"""

from fastapi import FastAPI, Body, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import sqlite3
from pathlib import Path
from typing import Optional

app = FastAPI(
    title="AI Activity Tracker Dashboard",
    description="Track and analyze your computer activity with AI-powered insights",
    version="2.0.0"
)

DB_PATH = Path("activity.db")

# Ensure database exists
def ensure_database():
    """Create database if it doesn't exist."""
    if not DB_PATH.exists():
        from database import init_database
        init_database()

ensure_database()

def get_db_connection():
    """Create a database connection with row factory."""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail="Database connection failed")

@app.get("/api/summary")
async def get_summary(date: Optional[str] = ""):
    """
    Get daily summary statistics.
    
    Args:
        date: Target date in YYYY-MM-DD format (defaults to today)
        
    Returns:
        Dictionary with hours spent in each category
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Use provided date or default to today
        target_date = date if date else datetime.now().date().isoformat()
        
        cursor.execute("""
            SELECT category, COUNT(*) as count, is_idle
            FROM activity_log
            WHERE DATE(timestamp) = ?
            GROUP BY category, is_idle
        """, (target_date,))
        
        rows = cursor.fetchall()
        
        # Calculate statistics (each entry = 5 seconds)
        SECONDS_PER_ENTRY = 5
        
        stats = {
            'Productivity': 0,
            'Entertainment': 0,
            'Social Media': 0,
            'Communication': 0,
            'Other': 0,
            'Idle': 0
        }
        
        for row in rows:
            category = row['category']
            count = row['count']
            is_idle = row['is_idle']
            
            seconds = count * SECONDS_PER_ENTRY
            
            if is_idle:
                stats['Idle'] += seconds
            else:
                stats[category] = stats.get(category, 0) + seconds
        
        # Convert to hours
        summary = {
            'focused_hours': round((stats['Productivity']) / 3600, 2),
            'distracted_hours': round((stats['Entertainment'] + stats['Social Media']) / 3600, 2),
            'communication_hours': round(stats['Communication'] / 3600, 2),
            'idle_hours': round(stats['Idle'] / 3600, 2),
            'other_hours': round(stats['Other'] / 3600, 2),
            'total_tracked_hours': round(sum(stats.values()) / 3600, 2)
        }
        
        return summary
    finally:
        conn.close()

@app.get("/api/timeline")
async def get_timeline(date: Optional[str] = ""):
    """
    Get hourly breakdown of activities for timeline visualization.
    
    Args:
        date: Target date in YYYY-MM-DD format (defaults to today)
        
    Returns:
        List of 24 hourly activity breakdowns
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        target_date = date if date else datetime.now().date().isoformat()
        
        cursor.execute("""
            SELECT 
                strftime('%H', timestamp) as hour,
                category,
                COUNT(*) as count,
                is_idle
            FROM activity_log
            WHERE DATE(timestamp) = ?
            GROUP BY hour, category, is_idle
            ORDER BY hour
        """, (target_date,))
        
        rows = cursor.fetchall()
        
        # Organize by hour
        timeline = {}
        SECONDS_PER_ENTRY = 5
        
        for row in rows:
            hour = int(row['hour'])
            category = row['category']
            count = row['count']
            is_idle = row['is_idle']
            
            if hour not in timeline:
                timeline[hour] = {
                    'hour': hour,
                    'Productivity': 0,
                    'Entertainment': 0,
                    'Social Media': 0,
                    'Communication': 0,
                    'Other': 0,
                    'Idle': 0
                }
            
            minutes = (count * SECONDS_PER_ENTRY) / 60
            
            if is_idle:
                timeline[hour]['Idle'] += minutes
            else:
                timeline[hour][category] += minutes
        
        # Convert to list and fill missing hours
        result = []
        for h in range(24):
            if h in timeline:
                result.append(timeline[h])
            else:
                result.append({
                    'hour': h,
                    'Productivity': 0,
                    'Entertainment': 0,
                    'Social Media': 0,
                    'Communication': 0,
                    'Other': 0,
                    'Idle': 0
                })
        
        return result
    finally:
        conn.close()

@app.get("/api/recent")
async def get_recent_activity(limit: int = 50, date: Optional[str] = ""):
    """
    Get recent activity entries.
    
    Args:
        limit: Maximum number of activities to return (default: 50)
        date: Target date in YYYY-MM-DD format (defaults to today)
        
    Returns:
        List of recent activities
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        target_date = date if date else datetime.now().date().isoformat()
        
        cursor.execute("""
            SELECT id, timestamp, app_name, window_title, category, is_idle
            FROM activity_log
            WHERE DATE(timestamp) = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (target_date, limit))
        
        rows = cursor.fetchall()
        
        activities = []
        for row in rows:
            activities.append({
                'id': row['id'],
                'timestamp': row['timestamp'],
                'app_name': row['app_name'],
                'window_title': row['window_title'],
                'category': row['category'],
                'is_idle': bool(row['is_idle'])
            })
        
        return activities
    finally:
        conn.close()

@app.get("/api/unique-activities")
async def get_unique_activities(date: Optional[str] = ""):
    """
    Get unique app and window title combinations for labeling.
    
    Args:
        date: Target date in YYYY-MM-DD format (defaults to today)
        
    Returns:
        List of unique activities grouped by instances
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        target_date = date if date else datetime.now().date().isoformat()
        
        cursor.execute("""
            SELECT app_name, window_title, category, COUNT(*) as instances
            FROM activity_log
            WHERE DATE(timestamp) = ?
            GROUP BY app_name, window_title
            ORDER BY instances DESC
        """, (target_date,))
        
        rows = cursor.fetchall()
        
        unique_activities = []
        for row in rows:
            unique_activities.append({
                'app_name': row['app_name'],
                'window_title': row['window_title'],
                'category': row['category'],
                'instances': row['instances']
            })
        
        return unique_activities
    finally:
        conn.close()

@app.put("/api/activity/batch")
async def batch_update_activity(payload: dict = Body(...)):
    """
    Update the category of all historical activities matching the app and title.
    
    Args:
        payload: Dictionary with app_name, window_title, and category
        
    Returns:
        Success status
    """
    app_name = payload.get("app_name")
    window_title = payload.get("window_title")
    new_category = payload.get("category")
    
    if app_name is None or window_title is None or new_category is None:
        raise HTTPException(status_code=400, detail="Missing required fields: app_name, window_title, category")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print(f"[API] Batch updating: app='{app_name}', title='{window_title}' → '{new_category}'")
        cursor.execute(
            "UPDATE activity_log SET category = ? WHERE app_name = ? AND window_title = ?",
            (new_category, app_name, window_title)
        )
        conn.commit()
        rows_updated = cursor.rowcount
        print(f"[API] Updated {rows_updated} rows")
        
        return {
            "success": rows_updated > 0,
            "rows_updated": rows_updated
        }
    except Exception as e:
        print(f"[API] Error updating activity batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

@app.post("/api/retrain")
async def retrain_model():
    """
    Trigger two-stage ML model retraining.
    
    Returns:
        Success status and any error messages
    """
    try:
        print("[API] Starting model retraining...")
        from train_model import train_two_stage_model
        success = train_two_stage_model()
        
        if success:
            print("[API] Model retraining completed successfully")
            return {"success": True}
        else:
            print("[API] Model retraining failed")
            return {"success": False, "error": "Training failed - check console for details"}
            
    except ImportError as e:
        error_msg = f"Import error: {str(e)}"
        print(f"[API] {error_msg}")
        return {"success": False, "error": error_msg}
    except Exception as e:
        import traceback
        error_msg = str(e)
        full_trace = traceback.format_exc()
        print(f"[API] Error triggering retrain: {error_msg}")
        print(f"[API] Full traceback:\n{full_trace}")
        return {"success": False, "error": error_msg}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main dashboard HTML."""
    html_path = Path("dashboard/index.html")
    if html_path.exists():
        return html_path.read_text(encoding='utf-8')
    raise HTTPException(status_code=404, detail="Dashboard not found. Please ensure dashboard/index.html exists.")

@app.get("/labeling", response_class=HTMLResponse)
async def read_labeling():
    """Serve the ML labeling dashboard HTML."""
    html_path = Path("dashboard/labeling.html")
    if html_path.exists():
        return html_path.read_text(encoding='utf-8')
    raise HTTPException(status_code=404, detail="Labeling dashboard not found. Please ensure dashboard/labeling.html exists.")

# Mount static files (must be last to avoid route conflicts)
app.mount("/static", StaticFiles(directory="dashboard"), name="static")

if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("🎯 AI Activity Tracker Dashboard")
    print("=" * 60)
    print("Starting server...")
    print("Dashboard: http://localhost:8000")
    print("Labeling:  http://localhost:8000/labeling")
    print("API Docs:  http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
