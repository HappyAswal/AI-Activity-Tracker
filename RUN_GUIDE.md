# 🚀 How to Run the Complete Project

## Quick Start (First Time Setup)

### Step 1: Install Dependencies

Open your terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

This installs all required Python packages.

---

### Step 2: Start the Activity Tracker

In your terminal, run:

```bash
python tracker.py
```

**What you'll see:**
```
Initializing AI Activity Tracker...
Database initialized.
Idle detection started.
Alert manager started.
Tracker running. Polling every 5 seconds...

[14:23:45] ACTIVE | Productivity    | vscode              | main.py
[14:23:50] ACTIVE | Entertainment   | spotify             | Playing Music
```

**Keep this terminal open!** The tracker needs to run continuously.

**Let it run for at least 2-3 hours** to collect enough data for ML training.

---

### Step 3: View the Dashboard (Optional)

Open a **NEW terminal** (keep tracker running in the first one) and run:

```bash
python app.py
```

**What you'll see:**
```
============================================================
🎯 AI Activity Tracker Dashboard
============================================================
Starting server...
Dashboard: http://localhost:8000
Labeling:  http://localhost:8000/labeling
API Docs:  http://localhost:8000/docs
============================================================
```

Open your browser and go to:
- **Main Dashboard:** http://localhost:8000
- **Labeling Interface:** http://localhost:8000/labeling
- **API Documentation:** http://localhost:8000/docs

---

### Step 4: Train ML Models (After 2-3 Hours)

After collecting enough data, open a **NEW terminal** and run:

```bash
python train_model.py
```

**What you'll see:**
```
======================================================================
TWO-STAGE ML MODEL TRAINING
======================================================================

[STAGE 1] Collecting training data...
Stage 1 data collected: 156 unique activities

Stage 1 Category Distribution:
  Productivity          78 (50.0%) ████████████████████████
  Entertainment         42 (26.9%) █████████████
  Social Media          18 (11.5%) █████
  Communication         12 ( 7.7%) ███
  Other                  6 ( 3.8%) █

[STAGE 1] Training model...
✅ Stage 1 training complete!

[STAGE 2] Training model...
✅ Stage 2 training complete!

✅ TRAINING COMPLETE!
```

---

### Step 5: Restart Tracker with ML

Stop the tracker (Ctrl+C in the tracker terminal) and restart it:

```bash
python tracker.py
```

Now it will use ML classification! You'll see:
```
Two-stage ML categorizer loaded. Using AI-powered categorization.
  Stage 1: TF-IDF + Logistic Regression
  Stage 2: TF-IDF + SVM (for video content)
```

---

## Daily Usage (After Setup)

### Option A: Just Track Activities

```bash
python tracker.py
```

That's it! The tracker will:
- Monitor your activities every 5 seconds
- Classify them using ML (or rules if not trained)
- Send alerts for distractions/breaks
- Store everything in the database

### Option B: Track + View Dashboard

**Terminal 1:**
```bash
python tracker.py
```

**Terminal 2:**
```bash
python app.py
```

Then open http://localhost:8000 in your browser.

---

## Testing & Diagnostics

### Test Classification Accuracy

```bash
python diagnose.py
```

**Output:**
```
======================================================================
RULE-BASED CATEGORIZATION TEST
======================================================================
✓ All tests passed
Score: 13/13 (100.0%)

======================================================================
TWO-STAGE ML CATEGORIZER
======================================================================
✓ Model loaded
Accuracy: 25/27 (92.6%)
```

### Interactive Testing

```bash
python diagnose.py interactive
```

Test your own app names and window titles:
```
App name (e.g., msedge.exe): chrome.exe
Window title: YouTube - Python Tutorial

  Cleaned: app='', title='youtube - python tutorial'
  Rule-based: Productivity
  ML-based: Productivity (confidence: 0.87)
```

### Compare Models

```bash
python compare_models.py
```

See which approach works best:
```
Rule-Based:       100.0%
Two-Stage ML:      92.6%

🏆 Winner: Rule-Based (need more training data for ML)
```

---

## Improving Accuracy

### 1. Label Corrections

1. Make sure dashboard is running: `python app.py`
2. Open http://localhost:8000/labeling
3. Fix any wrong categories
4. Click "Retrain AI & Sync"

### 2. Retrain Models

```bash
python train_model.py
```

### 3. Evaluate Performance

```bash
python train_model.py eval
```

---

## Common Commands Cheat Sheet

| Command | Purpose |
|---------|---------|
| `python tracker.py` | Start activity tracking |
| `python app.py` | Start web dashboard |
| `python train_model.py` | Train ML models |
| `python train_model.py eval` | Evaluate trained models |
| `python diagnose.py` | Run diagnostics |
| `python diagnose.py interactive` | Interactive testing |
| `python compare_models.py` | Compare all approaches |

---

## Stopping the Project

### Stop Tracker
Press `Ctrl+C` in the tracker terminal

### Stop Dashboard
Press `Ctrl+C` in the dashboard terminal

---

## Troubleshooting

### "No module named 'sklearn'"

Install dependencies:
```bash
pip install -r requirements.txt
```

### "Database not found"

The tracker creates it automatically. Just run:
```bash
python tracker.py
```

### "Not enough training data"

Run the tracker longer (2-3 hours minimum) before training:
```bash
python tracker.py
# Wait 2-3 hours...
python train_model.py
```

### "Port 8000 already in use"

Kill the existing process or change the port in `app.py`:
```python
uvicorn.run("app:app", host="0.0.0.0", port=8001, reload=True)
```

### Low ML Accuracy

1. Collect more data (run tracker longer)
2. Use labeling dashboard to fix mistakes
3. Retrain models
4. Check `TWO_STAGE_ML_GUIDE.md` for tuning tips

---

## Advanced Usage

### Run in Background (Windows)

```bash
# Start tracker in background
start /B python tracker.py

# Start dashboard in background
start /B python app.py
```

### Run in Background (Linux/Mac)

```bash
# Start tracker in background
nohup python tracker.py > tracker.log 2>&1 &

# Start dashboard in background
nohup python app.py > dashboard.log 2>&1 &
```

### Auto-start on Boot (Windows)

1. Create a batch file `start_tracker.bat`:
```batch
@echo off
cd C:\path\to\AISTRESS2
python tracker.py
```

2. Add to Windows Startup folder:
   - Press `Win+R`
   - Type `shell:startup`
   - Copy `start_tracker.bat` there

### View Logs

```bash
# View tracker output
tail -f tracker.log

# View dashboard output
tail -f dashboard.log
```

---

## Complete Workflow Example

### Day 1: Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Start tracking
python tracker.py
# Leave running all day...
```

### Day 2: Train ML

```bash
# Train models
python train_model.py

# Restart tracker with ML
python tracker.py
```

### Day 3: Refine

```bash
# Start dashboard
python app.py

# Open http://localhost:8000/labeling
# Fix mistakes, click "Retrain AI & Sync"

# Check accuracy
python compare_models.py
```

### Day 4+: Enjoy!

```bash
# Just run tracker
python tracker.py

# Optionally view dashboard
python app.py
```

---

## Quick Reference

### Minimum Requirements
- Python 3.7+
- 2-3 hours of tracked data for ML
- 30+ unique activities for Stage 1
- 20+ video activities for Stage 2

### Expected Accuracy
- Rule-based: 100% (on test cases)
- ML (30-50 samples): 70-80%
- ML (100-200 samples): 85-90%
- ML (500+ samples): 90-95%

### File Locations
- Database: `activity.db`
- Models: `models/stage1_classifier.pkl`, `models/stage2_classifier.pkl`
- Dashboard: `dashboard/`
- Logs: Console output (redirect to file if needed)

---

## Need Help?

1. Check `README.md` for full documentation
2. Check `TWO_STAGE_ML_GUIDE.md` for ML details
3. Check `PROJECT_STRUCTURE.md` for file overview
4. Run diagnostics: `python diagnose.py`

---

**Happy tracking! 🎯**
