"""
Two-Stage ML Model Training Script

Stage 1: Train on all activity data (5 categories)
Stage 2: Train on YouTube/video content (Productive vs Entertainment)
"""

import sqlite3
from pathlib import Path
from collections import Counter
from ml_categorizer import get_ml_categorizer

DB_PATH = Path("activity.db")


def collect_stage1_training_data():
    """
    Collect training data for Stage 1 from the database.
    Returns unique (app, title, category) tuples.
    """
    if not DB_PATH.exists():
        print("No database found. Run the tracker first to collect data.")
        return []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all activities with their categories
    cursor.execute("""
        SELECT app_name, window_title, category
        FROM activity_log
        WHERE category IS NOT NULL
        AND is_idle = 0
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        print("No activity data found in database.")
        return []
    
    # Deduplicate: Pick most frequent category for each (app, title) pair
    pair_counts = {}
    for app, title, cat in rows:
        key = (app, title)
        if key not in pair_counts:
            pair_counts[key] = {}
        if cat not in pair_counts[key]:
            pair_counts[key][cat] = 0
        pair_counts[key][cat] += 1
    
    unique_data = []
    for (app, title), cat_counts in pair_counts.items():
        best_cat = max(cat_counts.items(), key=lambda x: x[1])[0]
        unique_data.append((app, title, best_cat))
    
    return unique_data


def collect_stage2_training_data():
    """
    Collect training data for Stage 2 (YouTube/video content).
    
    This requires manual labeling of video content as 'Productive' or 'Entertainment'.
    For now, we'll use heuristics based on keywords.
    """
    if not DB_PATH.exists():
        return []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get YouTube/video activities
    cursor.execute("""
        SELECT DISTINCT app_name, window_title, category
        FROM activity_log
        WHERE (
            LOWER(window_title) LIKE '%youtube%' OR
            LOWER(window_title) LIKE '%video%' OR
            LOWER(window_title) LIKE '%vimeo%' OR
            LOWER(window_title) LIKE '%twitch%'
        )
        AND is_idle = 0
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return []
    
    # Use heuristics to label as Productive or Entertainment
    productive_keywords = [
        'tutorial', 'programming', 'coding', 'leetcode', 'algorithm',
        'python', 'java', 'javascript', 'c++', 'course', 'learn',
        'documentation', 'guide', 'lesson', 'lecture', 'education',
        'how to', 'explained', 'debugging', 'development', 'software'
    ]
    
    stage2_data = []
    for app, title, category in rows:
        title_lower = title.lower()
        
        # Check if it's educational/productive content
        is_productive = any(keyword in title_lower for keyword in productive_keywords)
        
        # If category is Productivity, likely productive
        if category == 'Productivity' or is_productive:
            label = 'Productive'
        else:
            label = 'Entertainment'
        
        stage2_data.append((app, title, label))
    
    # Deduplicate
    unique_stage2 = list(set(stage2_data))
    
    return unique_stage2


def train_two_stage_model():
    """Train both Stage 1 and Stage 2 models."""
    print("=" * 70)
    print("TWO-STAGE ML MODEL TRAINING")
    print("=" * 70)
    
    categorizer = get_ml_categorizer()
    
    # Stage 1 Training
    print("\n[STAGE 1] Collecting training data...")
    stage1_data = collect_stage1_training_data()
    
    if len(stage1_data) < 30:
        print(f"\n⚠️  Not enough data for Stage 1. Need at least 30 samples, got {len(stage1_data)}.")
        print("Run the tracker for a while to collect more activity data.")
        return False
    
    print(f"\nStage 1 data collected: {len(stage1_data)} unique activities")
    
    # Show distribution
    category_counts = Counter([cat for _, _, cat in stage1_data])
    print("\nStage 1 Category Distribution:")
    for category, count in category_counts.most_common():
        percentage = (count / len(stage1_data)) * 100
        bar = "█" * int(percentage / 2)
        print(f"  {category:20} {count:4} ({percentage:5.1f}%) {bar}")
    
    print("\n[STAGE 1] Training model...")
    success1 = categorizer.train_stage1(stage1_data)
    
    if not success1:
        print("\n❌ Stage 1 training failed.")
        return False
    
    print("✅ Stage 1 training complete!")
    
    # Stage 2 Training
    print("\n" + "=" * 70)
    print("[STAGE 2] Collecting YouTube/video training data...")
    stage2_data = collect_stage2_training_data()
    
    if len(stage2_data) < 20:
        print(f"\n⚠️  Not enough video data for Stage 2. Got {len(stage2_data)} samples.")
        print("Stage 2 will be skipped. Use the labeling dashboard to add more video content.")
        print("Stage 1 model will still work for basic categorization.")
    else:
        print(f"\nStage 2 data collected: {len(stage2_data)} video activities")
        
        # Show distribution
        label_counts = Counter([label for _, _, label in stage2_data])
        print("\nStage 2 Label Distribution:")
        for label, count in label_counts.most_common():
            percentage = (count / len(stage2_data)) * 100
            bar = "█" * int(percentage / 2)
            print(f"  {label:20} {count:4} ({percentage:5.1f}%) {bar}")
        
        print("\n[STAGE 2] Training model...")
        success2 = categorizer.train_stage2(stage2_data)
        
        if success2:
            print("✅ Stage 2 training complete!")
        else:
            print("⚠️  Stage 2 training failed, but Stage 1 is ready.")
    
    # Save models
    print("\n" + "=" * 70)
    print("Saving models...")
    categorizer.save_models()
    
    print("\n" + "=" * 70)
    print("✅ TRAINING COMPLETE!")
    print("=" * 70)
    print("\nThe tracker will now use the two-stage ML categorization:")
    print("  Stage 1: TF-IDF + Logistic Regression (5 categories)")
    if categorizer.stage2_trained:
        print("  Stage 2: TF-IDF + SVM (Productive vs Entertainment for videos)")
    print("\nRestart the tracker to use the new models.")
    print("=" * 70)
    
    return True


def evaluate_models():
    """Evaluate model performance on test data."""
    print("\n" + "=" * 70)
    print("MODEL EVALUATION")
    print("=" * 70)
    
    categorizer = get_ml_categorizer()
    
    if not categorizer.stage1_trained:
        print("\n⚠️  No trained models found. Train first with 'python train_model.py'")
        return
    
    # Test cases
    test_cases = [
        ("msedge.exe", "Stack Overflow - Python question", "Productivity"),
        ("msedge.exe", "YouTube - Leetcode Tutorial", "Productivity"),
        ("msedge.exe", "YouTube - Music Video", "Entertainment"),
        ("msedge.exe", "Netflix - Movie", "Entertainment"),
        ("msedge.exe", "Instagram - Feed", "Social Media"),
        ("slack.exe", "Slack - Team Chat", "Communication"),
        ("code.exe", "Visual Studio Code", "Productivity"),
        ("spotify.exe", "Spotify - Music", "Entertainment"),
    ]
    
    print("\nTesting on sample cases:")
    correct = 0
    
    for app, title, expected in test_cases:
        result = categorizer.predict(app, title)
        status = "✓" if result == expected else "✗"
        
        print(f"\n{status} {app:20} | {title[:40]}")
        print(f"  Expected: {expected:20} Got: {result}")
        
        if result == expected:
            correct += 1
    
    accuracy = (correct / len(test_cases)) * 100
    print(f"\n{'=' * 70}")
    print(f"Accuracy: {correct}/{len(test_cases)} ({accuracy:.1f}%)")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "eval":
        evaluate_models()
    else:
        train_two_stage_model()
