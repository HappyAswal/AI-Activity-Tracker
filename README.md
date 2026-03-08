# AI Activity Tracker - Two-Stage ML System

An AI-powered tool that tracks user activity, detects distractions, and helps improve focus using advanced two-stage machine learning.

## 🎯 Current Status: Enhanced with Two-Stage ML ✅

### Core Features ✅
- Real-time activity monitoring with idle detection
- Smart distraction alerts and break reminders
- Beautiful web dashboard with analytics
- Local, private data storage

### 🆕 Two-Stage ML Classification System ✅
- **Stage 1**: TF-IDF + Logistic Regression (5 categories)
- **Stage 2**: TF-IDF + SVM (Productive vs Entertainment for videos)
- Hot-reload capability for instant model updates
- 90-95% accuracy with sufficient training data

## Quick Start

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the tracker to collect initial data:
```bash
python tracker.py
```

3. After collecting data (2+ hours), train the ML models:
```bash
python train_model.py
```

4. Start the web dashboard:
```bash
python app.py
```

5. Open http://localhost:8000

## Two-Stage ML System

### Why Two Stages?

Traditional single-stage classifiers struggle with context-dependent content like YouTube:
- "YouTube - Python Tutorial" should be **Productivity**
- "YouTube - Music Video" should be **Entertainment**

Our two-stage system solves this:

**Stage 1** (TF-IDF + Logistic Regression)
- Classifies into 5 main categories
- Handles app-level and platform-level classification
- 1000 TF-IDF features with 1-3 n-grams

**Stage 2** (TF-IDF + SVM)
- Refines video/YouTube content
- Binary classification: Productive vs Entertainment
- Only runs when needed (YouTube, Vimeo, etc.)

### Training the Models

```bash
# Train both stages
python train_model.py

# Evaluate performance
python train_model.py eval

# Compare with rule-based
python compare_models.py
```

**Requirements:**
- Stage 1: Minimum 30 samples (recommended: 100+)
- Stage 2: Minimum 20 video samples (recommended: 50+)

### Expected Accuracy

| Training Data | Accuracy |
|---------------|----------|
| 30-50 samples | 70-80% |
| 100-200 samples | 85-90% |
| 500+ samples | 90-95% |
| 1000+ samples | 95%+ |

## Project Structure

### Core Files
- `tracker.py` - Main daemon that monitors activity
- `database.py` - SQLite database operations
- `categorizer.py` - Enhanced rule-based categorization with word boundaries
- `alerts.py` - Smart notification system

### ML System
- `ml_categorizer.py` - Two-stage ML classification
- `train_model.py` - Training script for both stages
- `compare_models.py` - Model comparison tool
- `diagnose.py` - Diagnostic and testing tool

### Dashboard
- `app.py` - FastAPI web server
- `dashboard/` - Frontend files (HTML, CSS, JS)

### Models
- `models/stage1_classifier.pkl` - Stage 1 model
- `models/stage2_classifier.pkl` - Stage 2 model

## Features

### Activity Tracking
- Real-time monitoring every 5 seconds
- Idle detection (2-minute threshold)
- Smart data cleaning and normalization
- Local SQLite storage

### ML Classification
- Two-stage classification system
- Confidence-based fallback to rules
- Hot-reload for instant model updates
- Handles imbalanced data automatically

### Smart Alerts
- Distraction alerts (15-minute threshold)
- Break reminders (90-minute threshold)
- Interactive OS dialogs
- Configurable thresholds

### Web Dashboard
- Real-time statistics with auto-refresh
- Activity distribution pie chart
- Hourly timeline with stacked bars
- Recent activity feed
- Data labeling interface
- One-click model retraining

## Labeling & Retraining

1. Open http://localhost:8000/labeling
2. Correct any misclassified activities
3. Click "Retrain AI & Sync"
4. Models update automatically (no restart needed!)

## Diagnostic Tools

### Test Categorization
```bash
# Run all diagnostics
python diagnose.py

# Interactive testing
python diagnose.py interactive
```

### Compare Models
```bash
python compare_models.py
```

Shows accuracy comparison:
- Rule-based categorization
- Old ML (Naive Bayes)
- New ML (Two-stage)

## Configuration

### Alert Thresholds
Edit `alerts.py`:
```python
DISTRACTION_THRESHOLD = 15  # Minutes
PRODUCTIVITY_THRESHOLD = 90  # Minutes
CHECK_INTERVAL = 60  # Seconds
```

### ML Confidence Thresholds
Edit `ml_categorizer.py`:
```python
if stage1_confidence < 0.4:  # Adjust threshold
    return rule_based_categorize()
```

### Add Custom Keywords
Edit `categorizer.py` to add your specific apps/sites to the keyword lists.

## Documentation

- `TWO_STAGE_ML_GUIDE.md` - Comprehensive ML system guide
- `fix_classification.md` - Troubleshooting classification issues

## Technical Details

### Stage 1: Logistic Regression
- Multi-class classification (5 categories)
- TF-IDF features with 1-3 n-grams
- Balanced class weights
- Multinomial solver

### Stage 2: SVM
- Binary classification (Productive vs Entertainment)
- Linear kernel for speed
- Probability estimates enabled
- Only runs for video content

### Performance
- Training: 1-5 seconds
- Prediction: <2ms per activity
- Memory: ~3MB for both models

## Privacy

- All data stored locally in SQLite
- No data leaves your computer
- No external API calls
- Open source and auditable

## Requirements

```
psutil==5.9.8
pygetwindow==0.0.9
pynput==1.7.6
fastapi==0.109.0
uvicorn==0.27.0
plyer==2.1.0
pytest==8.0.0
scikit-learn==1.4.0
pandas==2.2.0
numpy==1.26.3
```

## Platform Support

- Windows (fully tested)
- Linux (should work, may need adjustments)
- macOS (should work, may need adjustments)

## Future Enhancements

- [ ] BERT/Transformer models for higher accuracy
- [ ] Active learning for continuous improvement
- [ ] Multi-label classification
- [ ] Temporal features (time of day, day of week)
- [ ] User-specific model training
- [ ] Export reports (PDF, CSV)
- [ ] Mobile app companion

## Contributing

Contributions welcome! Areas of interest:
- Model improvements
- New features
- Bug fixes
- Documentation
- Platform support

## License

MIT License - See LICENSE file for details
