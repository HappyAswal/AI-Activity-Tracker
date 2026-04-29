@echo off
echo ============================================
echo   AI Activity Tracker - Setup
echo ============================================
echo.

:: Check Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.9+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo [2/3] Initializing database...
python -c "from database import init_database; init_database(); print('Database ready.')"

echo.
echo [3/3] Setup complete!
echo.
echo ============================================
echo   HOW TO RUN
echo ============================================
echo.
echo   Open TWO terminal windows:
echo.
echo   Terminal 1 - Start the tracker:
echo     python tracker.py
echo.
echo   Terminal 2 - Start the dashboard:
echo     python app.py
echo.
echo   Then open: http://localhost:8000
echo ============================================
echo.
pause
