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

```
User Activity
     ↓
┌────────────────────────────────────┐
│  STAGE 1: Primary Classification  │
│  TF-IDF + Logistic Regression      │
│                                    │
│  5 Categories:                     │
│  • Productivity                    │
│  • Entertainment                   │
│  • Social Media                    │
│  • Communication                   │
│  • Other                           │
└────────────────────────────────────┘
     ↓
Is it YouTube/Video content?
     ↓ Yes
┌────────────────────────────────────┐
│  STAGE 2: Content Refinement       │
│  TF-IDF + SVM                      │
│                                    │
│  2 Categories:                     │
│  • Productive (tutorials, courses) │
│  • Entertainment (music, gaming)   │
└────────────────────────────────────┘
     ↓
Final Category
```

**Stage 1** (TF-IDF + Logistic Regression)
- Classifies into 5 main categories
- Handles app-level and platform-level classification
- 1000 TF-IDF features with 1-3 n-grams
- Multinomial solver with balanced class weights
- Fast training (1-5 seconds) and prediction (<1ms)

**Stage 2** (TF-IDF + SVM)
- Refines video/YouTube content
- Binary classification: Productive vs Entertainment
- 800 TF-IDF features with linear kernel
- Only runs when needed (YouTube, Vimeo, etc.)
- Prediction time: <2ms total (both stages)

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
- Run tracker for 2-3 hours minimum before training

**What happens during training:**
```
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
```

### Expected Accuracy

| Training Data | Stage 1 | Stage 2 | Overall |
|---------------|---------|---------|---------|
| 30-50 samples | 70-80% | N/A | 70-80% |
| 100-200 samples | 85-90% | 75-85% | 85-90% |
| 500+ samples | 90-95% | 85-95% | 90-95% |
| 1000+ samples | 95%+ | 90%+ | 95%+ |

### Confidence Thresholds

The system uses confidence scoring to decide when to use ML vs rule-based fallback:

```python
# Stage 1: If confidence < 0.4, fallback to rules
if stage1_confidence < 0.4:
    return rule_based_categorize()

# Stage 2: If confidence > 0.5, use Stage 2 prediction
if stage2_confidence > 0.5:
    return stage2_prediction
else:
    return stage1_prediction
```

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

### Hyperparameter Tuning

**Increase TF-IDF features for complex patterns:**
```python
TfidfVectorizer(
    max_features=2000,  # Increase from 1000
    ngram_range=(1, 4),  # Add 4-grams
)
```

**Adjust confidence thresholds for stricter predictions:**
```python
if stage1_confidence < 0.5:  # Increase from 0.4
    return rule_based_categorize()
```

**Change SVM kernel for non-linear patterns:**
```python
SVC(
    kernel='rbf',  # Change from 'linear'
    gamma='scale'
)
```

### Add Custom Keywords
Edit `categorizer.py` to add your specific apps/sites to the keyword lists.

## Documentation

- `README.md` - Complete project documentation (this file)

## Troubleshooting

### Low ML Accuracy
**Causes:** Not enough training data, imbalanced categories, poor quality labels

**Solutions:**
1. Collect more data (run tracker longer)
2. Use labeling dashboard to correct mistakes
3. Ensure diverse activities across all categories

### Stage 2 Not Training
**Cause:** Not enough video/YouTube content

**Solution:**
- Watch some YouTube tutorials while tracker is running
- Use labeling dashboard to manually add video entries
- Stage 1 will still work without Stage 2

### Model Not Loading
**Cause:** Model files corrupted or missing

**Solution:**
```bash
python train_model.py  # Retrain from scratch
```

## Technical Details

### Stage 1: Logistic Regression
- Multi-class classification (5 categories)
- TF-IDF features: 1000 max features, 1-3 n-grams
- Balanced class weights for imbalanced data
- Multinomial solver (lbfgs)
- Sublinear TF scaling
- Max DF 0.8 to filter common words

**Configuration:**
```python
TfidfVectorizer(
    max_features=1000,
    ngram_range=(1, 3),
    min_df=2,
    max_df=0.8,
    sublinear_tf=True
)

LogisticRegression(
    max_iter=1000,
    multi_class='multinomial',
    solver='lbfgs',
    class_weight='balanced'
)
```

### Stage 2: SVM
- Binary classification (Productive vs Entertainment)
- TF-IDF features: 800 max features, 1-3 n-grams
- Linear kernel for speed and text data
- Probability estimates enabled
- Balanced class weights

**Configuration:**
```python
TfidfVectorizer(
    max_features=800,
    ngram_range=(1, 3),
    min_df=2,
    max_df=0.8,
    sublinear_tf=True
)

SVC(
    kernel='linear',
    C=1.0,
    class_weight='balanced',
    probability=True
)
```

### Performance
- Training: 1-5 seconds (Stage 1), 0.5-2 seconds (Stage 2)
- Prediction: <1ms (Stage 1 only), <2ms (both stages)
- Memory: ~3MB for both models
- CPU overhead: <1%

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
