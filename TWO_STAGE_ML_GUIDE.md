# Two-Stage ML Classification System

## Overview

The new classification system uses a sophisticated two-stage approach for better accuracy:

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

## Why Two Stages?

### Problem with Single-Stage Classification

YouTube and video platforms are tricky:
- "YouTube - Python Tutorial" → Should be **Productivity**
- "YouTube - Music Video" → Should be **Entertainment**

A single model struggles to distinguish these because both contain "YouTube".

### Solution: Two-Stage Approach

**Stage 1** handles platform/app-level classification
**Stage 2** refines video content based on educational value

## Technical Details

### Stage 1: TF-IDF + Logistic Regression

**Why Logistic Regression?**
- Excellent for multi-class text classification
- Fast training and prediction
- Handles imbalanced data well with `class_weight='balanced'`
- Provides probability estimates for confidence scoring

**Features:**
- TF-IDF vectorization with 1000 features
- N-grams (1-3): Captures "stack overflow", "visual studio code"
- Sublinear TF scaling: Reduces impact of very frequent words
- Max DF 0.8: Filters out overly common words

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
    C=1.0,
    class_weight='balanced'
)
```

### Stage 2: TF-IDF + SVM

**Why SVM?**
- Excellent for binary classification
- Works well with high-dimensional text data
- Linear kernel is fast and effective for text
- Robust to overfitting

**Features:**
- TF-IDF vectorization with 800 features
- N-grams (1-3): Captures educational phrases
- Probability estimates enabled for confidence scoring

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

## Usage

### 1. Collect Data

Run the tracker to collect activity data:

```bash
python tracker.py
```

Let it run for at least 2-3 hours to collect diverse activities.

### 2. Label Data (Optional but Recommended)

1. Start the dashboard:
   ```bash
   python app.py
   ```

2. Open http://localhost:8000/labeling

3. Correct any misclassifications

4. This improves training data quality

### 3. Train Models

```bash
python train_model.py
```

**Requirements:**
- Stage 1: Minimum 30 unique activities (recommended: 100+)
- Stage 2: Minimum 20 video activities (recommended: 50+)

**Output:**
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
Stage 1 trained on 156 samples
✅ Stage 1 training complete!

======================================================================
[STAGE 2] Collecting YouTube/video training data...
Stage 2 data collected: 34 video activities

Stage 2 Label Distribution:
  Productive            22 (64.7%) ████████████████████████████████
  Entertainment         12 (35.3%) █████████████████

[STAGE 2] Training model...
Stage 2 trained on 34 samples
✅ Stage 2 training complete!

======================================================================
Saving models...
Stage 1 model saved to models/stage1_classifier.pkl
Stage 2 model saved to models/stage2_classifier.pkl

======================================================================
✅ TRAINING COMPLETE!
======================================================================
```

### 4. Restart Tracker

The tracker will automatically use the new models:

```bash
python tracker.py
```

You'll see:
```
Two-stage ML categorizer loaded. Using AI-powered categorization.
  Stage 1: TF-IDF + Logistic Regression
  Stage 2: TF-IDF + SVM (for video content)
```

## Evaluation

### Compare Models

```bash
python compare_models.py
```

This compares:
1. Rule-based categorization
2. Old ML (Naive Bayes)
3. New ML (Two-stage)

**Example Output:**
```
================================================================================
                    MODEL COMPARISON
================================================================================

Rule-Based:               92.3%
Old ML (Naive Bayes):     85.7%
New ML (2-Stage):         96.2%

🏆 Winner: New Two-Stage ML System!
   Improvement: +3.9%
```

### Test Specific Cases

```bash
python train_model.py eval
```

## Expected Accuracy

| Data Amount | Stage 1 Accuracy | Stage 2 Accuracy | Overall |
|-------------|------------------|------------------|---------|
| 30-50 samples | 70-80% | N/A | 70-80% |
| 100-200 samples | 85-90% | 75-85% | 85-90% |
| 500+ samples | 90-95% | 85-95% | 90-95% |
| 1000+ samples | 95%+ | 90%+ | 95%+ |

## Confidence Thresholds

The system uses confidence scoring to decide when to use ML vs rule-based fallback:

```python
# Stage 1
if stage1_confidence < 0.4:
    return rule_based_categorize()  # Low confidence, use rules

# Stage 2
if stage2_confidence > 0.5:
    return stage2_prediction  # High confidence, use Stage 2
else:
    return stage1_prediction  # Low confidence, stick with Stage 1
```

## Troubleshooting

### Issue: Low Accuracy

**Causes:**
- Not enough training data
- Imbalanced categories
- Poor quality labels

**Solutions:**
1. Collect more data (run tracker longer)
2. Use labeling dashboard to correct mistakes
3. Ensure diverse activities across all categories

### Issue: Stage 2 Not Training

**Cause:** Not enough video/YouTube content

**Solution:**
- Watch some YouTube tutorials while tracker is running
- Use labeling dashboard to manually add video entries
- Stage 1 will still work without Stage 2

### Issue: Model Not Loading

**Cause:** Model files corrupted or missing

**Solution:**
```bash
# Retrain from scratch
python train_model.py
```

## Advanced: Hyperparameter Tuning

### Increase Features

For more complex patterns:

```python
# In ml_categorizer.py
TfidfVectorizer(
    max_features=2000,  # Increase from 1000
    ngram_range=(1, 4),  # Add 4-grams
)
```

### Adjust Confidence Thresholds

For stricter ML predictions:

```python
# In ml_categorizer.py, predict() method
if stage1_confidence < 0.5:  # Increase from 0.4
    return rule_based_categorize()
```

### Change SVM Kernel

For non-linear patterns:

```python
# In ml_categorizer.py
SVC(
    kernel='rbf',  # Change from 'linear'
    gamma='scale'
)
```

## Model Files

- `models/stage1_classifier.pkl` - Stage 1 model (5 categories)
- `models/stage2_classifier.pkl` - Stage 2 model (2 categories)

Both files are automatically reloaded when modified (hot-reload feature).

## API Integration

The dashboard automatically uses the new models. No changes needed!

The `/api/retrain` endpoint now triggers two-stage training:

```javascript
// In dashboard
fetch('/api/retrain', { method: 'POST' })
```

## Performance

**Training Time:**
- Stage 1: 1-5 seconds (100-500 samples)
- Stage 2: 0.5-2 seconds (20-100 samples)

**Prediction Time:**
- Stage 1 only: <1ms
- Stage 1 + Stage 2: <2ms

**Memory Usage:**
- Stage 1 model: ~500KB - 2MB
- Stage 2 model: ~300KB - 1MB

## Future Improvements

1. **BERT/Transformer Models**
   - Much higher accuracy
   - Requires more compute
   - Better context understanding

2. **Active Learning**
   - Automatically identify uncertain predictions
   - Request user labels for those cases
   - Continuously improve

3. **Multi-label Classification**
   - Activities can have multiple categories
   - E.g., "Slack - Code Review" → Communication + Productivity

4. **Temporal Features**
   - Time of day
   - Day of week
   - Activity duration

5. **User-Specific Models**
   - Train separate models per user
   - Personalized categorization

## References

- [Scikit-learn Logistic Regression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html)
- [Scikit-learn SVM](https://scikit-learn.org/stable/modules/svm.html)
- [TF-IDF Vectorization](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
