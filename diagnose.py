"""
Diagnostic tool to test and debug categorization issues.
"""

import sqlite3
from pathlib import Path
from categorizer import categorize_activity, DataCleaner
from collections import Counter

DB_PATH = Path("activity.db")

def test_rule_based_categorization():
    """Test rule-based categorizer with common scenarios."""
    print("=" * 70)
    print("RULE-BASED CATEGORIZATION TEST")
    print("=" * 70)
    
    test_cases = [
        # (app_name, window_title, expected_category)
        ("msedge.exe", "Stack Overflow - Python question - Google Chrome", "Productivity"),
        ("msedge.exe", "YouTube - Coding Tutorial", "Productivity"),
        ("msedge.exe", "YouTube - Music Video", "Entertainment"),
        ("msedge.exe", "Netflix - Watching Movie", "Entertainment"),
        ("msedge.exe", "Instagram - Feed", "Social Media"),
        ("msedge.exe", "Facebook - Home", "Social Media"),
        ("slack.exe", "Slack - Team Chat", "Communication"),
        ("code.exe", "Visual Studio Code - main.py", "Productivity"),
        ("spotify.exe", "Spotify - Playing Music", "Entertainment"),
        ("chrome.exe", "LeetCode - Problem Solving", "Productivity"),
        ("chrome.exe", "GitHub - Repository", "Productivity"),
        ("msedge.exe", "New Tab", "Other"),
        ("explorer.exe", "File Explorer", "Other"),
    ]
    
    correct = 0
    total = len(test_cases)
    
    for app, title, expected in test_cases:
        result = categorize_activity(app, title)
        status = "✓" if result == expected else "✗"
        
        clean_app, clean_title = DataCleaner.clean(app, title)
        
        print(f"\n{status} App: {app}")
        print(f"  Title: {title}")
        print(f"  Cleaned: app='{clean_app}', title='{clean_title}'")
        print(f"  Expected: {expected}")
        print(f"  Got: {result}")
        
        if result == expected:
            correct += 1
    
    print(f"\n{'=' * 70}")
    print(f"Score: {correct}/{total} ({correct/total*100:.1f}%)")
    print(f"{'=' * 70}\n")

def test_ml_categorization():
    """Test ML categorizer if model exists."""
    print("=" * 70)
    print("ML CATEGORIZATION TEST")
    print("=" * 70)
    
    try:
        from ml_categorizer import get_ml_categorizer
        
        categorizer = get_ml_categorizer()
        
        if not categorizer.is_trained:
            print("\n⚠️  ML model not trained yet.")
            print("Run 'python train_model.py' after collecting some data.\n")
            return
        
        print(f"\n✓ Model loaded successfully")
        print(f"  Model path: models/activity_classifier.pkl")
        
        test_cases = [
            ("msedge.exe", "Stack Overflow - Python question", "Productivity"),
            ("msedge.exe", "YouTube - Music Video", "Entertainment"),
            ("msedge.exe", "Instagram - Feed", "Social Media"),
            ("code.exe", "Visual Studio Code", "Productivity"),
        ]
        
        correct = 0
        total = len(test_cases)
        
        for app, title, expected in test_cases:
            result = categorizer.predict(app, title)
            status = "✓" if result == expected else "✗"
            
            # Get confidence
            text = categorizer.preprocess_text(app, title)
            try:
                probs = categorizer.model.predict_proba([text])[0]
                confidence = max(probs)
                pred_idx = probs.argmax()
                categories = categorizer.model.classes_
                
                print(f"\n{status} App: {app}")
                print(f"  Title: {title}")
                print(f"  Preprocessed: '{text}'")
                print(f"  Expected: {expected}")
                print(f"  Got: {result} (confidence: {confidence:.2%})")
                print(f"  All probabilities:")
                for cat, prob in zip(categories, probs):
                    print(f"    {cat:20} {prob:.2%}")
                
                if result == expected:
                    correct += 1
            except:
                print(f"\n{status} App: {app}")
                print(f"  Title: {title}")
                print(f"  Expected: {expected}")
                print(f"  Got: {result}")
        
        print(f"\n{'=' * 70}")
        print(f"Score: {correct}/{total} ({correct/total*100:.1f}%)")
        print(f"{'=' * 70}\n")
        
    except ImportError:
        print("\n⚠️  ML libraries not installed.")
        print("Install with: pip install scikit-learn pandas numpy\n")

def analyze_database():
    """Analyze existing database for classification issues."""
    print("=" * 70)
    print("DATABASE ANALYSIS")
    print("=" * 70)
    
    if not DB_PATH.exists():
        print("\n⚠️  No database found. Run tracker.py first to collect data.\n")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Category distribution
    cursor.execute("""
        SELECT category, COUNT(*) as count 
        FROM activity_log 
        GROUP BY category 
        ORDER BY count DESC
    """)
    
    print("\n📊 Category Distribution:")
    rows = cursor.fetchall()
    total = sum(row[1] for row in rows)
    
    for category, count in rows:
        percentage = (count / total * 100) if total > 0 else 0
        bar = "█" * int(percentage / 2)
        print(f"  {category:20} {count:6} ({percentage:5.1f}%) {bar}")
    
    # Most common apps
    cursor.execute("""
        SELECT app_name, COUNT(*) as count 
        FROM activity_log 
        GROUP BY app_name 
        ORDER BY count DESC 
        LIMIT 10
    """)
    
    print("\n📱 Top 10 Apps:")
    for app, count in cursor.fetchall():
        print(f"  {app:30} {count:6} entries")
    
    # Recent misclassifications (check for "Other" category)
    cursor.execute("""
        SELECT app_name, window_title, category, COUNT(*) as count
        FROM activity_log
        WHERE category = 'Other'
        GROUP BY app_name, window_title
        ORDER BY count DESC
        LIMIT 10
    """)
    
    print("\n⚠️  Top 10 'Other' Classifications (potential misclassifications):")
    for app, title, cat, count in cursor.fetchall():
        print(f"  [{count:4}x] {app:20} | {title[:40]}")
    
    conn.close()
    print()

def interactive_test():
    """Interactive testing mode."""
    print("=" * 70)
    print("INTERACTIVE TEST MODE")
    print("=" * 70)
    print("\nTest your own app names and window titles.")
    print("Type 'quit' to exit.\n")
    
    while True:
        try:
            app = input("App name (e.g., msedge.exe): ").strip()
            if app.lower() == 'quit':
                break
            
            title = input("Window title: ").strip()
            if title.lower() == 'quit':
                break
            
            # Test rule-based
            rule_result = categorize_activity(app, title)
            clean_app, clean_title = DataCleaner.clean(app, title)
            
            print(f"\n  Cleaned: app='{clean_app}', title='{clean_title}'")
            print(f"  Rule-based: {rule_result}")
            
            # Test ML if available
            try:
                from ml_categorizer import get_ml_categorizer
                categorizer = get_ml_categorizer()
                if categorizer.is_trained:
                    ml_result = categorizer.predict(app, title)
                    text = categorizer.preprocess_text(app, title)
                    probs = categorizer.model.predict_proba([text])[0]
                    confidence = max(probs)
                    print(f"  ML-based: {ml_result} (confidence: {confidence:.2%})")
            except:
                pass
            
            print()
            
        except KeyboardInterrupt:
            break
        except EOFError:
            break
    
    print("\nExiting interactive mode.\n")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_test()
    else:
        test_rule_based_categorization()
        test_ml_categorization()
        analyze_database()
        
        print("\n💡 Tips:")
        print("  - Run 'python diagnose.py interactive' for interactive testing")
        print("  - Check categorizer.py to add more keywords")
        print("  - Use the labeling dashboard to correct misclassifications")
        print("  - Retrain the ML model after labeling data\n")
