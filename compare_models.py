"""
Compare old vs new ML categorization systems.
"""

from categorizer import categorize_activity as rule_based

# Test cases with expected results
TEST_CASES = [
    # Format: (app, title, expected_category)
    
    # Productivity - Coding
    ("code.exe", "Visual Studio Code - main.py", "Productivity"),
    ("pycharm64.exe", "PyCharm - project.py", "Productivity"),
    ("msedge.exe", "Stack Overflow - Python question", "Productivity"),
    ("msedge.exe", "GitHub - Repository", "Productivity"),
    ("msedge.exe", "LeetCode - Two Sum Problem", "Productivity"),
    
    # Productivity - YouTube Educational
    ("msedge.exe", "YouTube - Python Tutorial for Beginners", "Productivity"),
    ("msedge.exe", "YouTube - Leetcode Graph DFS Explained", "Productivity"),
    ("msedge.exe", "YouTube - C++ Debugging Tutorial", "Productivity"),
    ("msedge.exe", "YouTube - How to use Docker", "Productivity"),
    
    # Entertainment - YouTube
    ("msedge.exe", "YouTube - Funny Cat Compilation", "Entertainment"),
    ("msedge.exe", "YouTube - MrBeast Challenge Video", "Entertainment"),
    ("msedge.exe", "YouTube - Music Video 2024", "Entertainment"),
    ("msedge.exe", "YouTube - Gaming Highlights", "Entertainment"),
    
    # Entertainment - Streaming
    ("msedge.exe", "Netflix - Watching Movie", "Entertainment"),
    ("spotify.exe", "Spotify - Playing Music", "Entertainment"),
    ("msedge.exe", "Twitch - Gaming Stream", "Entertainment"),
    
    # Social Media
    ("msedge.exe", "Instagram - Feed", "Social Media"),
    ("msedge.exe", "Facebook - Home", "Social Media"),
    ("msedge.exe", "Twitter - Timeline", "Social Media"),
    ("msedge.exe", "Reddit - r/programming", "Social Media"),
    
    # Communication
    ("slack.exe", "Slack - Team Chat", "Communication"),
    ("teams.exe", "Microsoft Teams - Meeting", "Communication"),
    ("msedge.exe", "Gmail - Inbox", "Communication"),
    ("zoom.exe", "Zoom - Video Call", "Communication"),
    
    # Other
    ("explorer.exe", "File Explorer", "Other"),
    ("msedge.exe", "New Tab", "Other"),
]


def test_rule_based():
    """Test rule-based categorizer."""
    print("=" * 70)
    print("RULE-BASED CATEGORIZER")
    print("=" * 70)
    
    correct = 0
    total = len(TEST_CASES)
    
    for app, title, expected in TEST_CASES:
        result = rule_based(app, title)
        status = "✓" if result == expected else "✗"
        
        if result != expected:
            print(f"{status} {title[:50]}")
            print(f"  Expected: {expected:20} Got: {result}")
        
        if result == expected:
            correct += 1
    
    accuracy = (correct / total) * 100
    print(f"\nAccuracy: {correct}/{total} ({accuracy:.1f}%)")
    return accuracy


def test_old_ml():
    """Test old ML categorizer (deprecated - now using two-stage)."""
    print("\n" + "=" * 70)
    print("OLD ML CATEGORIZER (Deprecated)")
    print("=" * 70)
    print("\n⚠️  Old single-stage ML has been replaced by two-stage system.")
    return 0


def test_new_ml():
    """Test new two-stage ML categorizer."""
    print("\n" + "=" * 70)
    print("TWO-STAGE ML CATEGORIZER")
    print("=" * 70)
    
    try:
        from ml_categorizer import get_ml_categorizer
        categorizer = get_ml_categorizer()
        
        if not categorizer.stage1_trained:
            print("\n⚠️  ML model not trained.")
            print("Run: python train_model.py")
            return 0
        
        correct = 0
        total = len(TEST_CASES)
        errors = []
        
        for app, title, expected in TEST_CASES:
            result = categorizer.predict(app, title)
            status = "✓" if result == expected else "✗"
            
            if result != expected:
                errors.append((app, title, expected, result))
                print(f"{status} {title[:50]}")
                print(f"  Expected: {expected:20} Got: {result}")
            
            if result == expected:
                correct += 1
        
        accuracy = (correct / total) * 100
        print(f"\nAccuracy: {correct}/{total} ({accuracy:.1f}%)")
        
        # Show Stage 2 usage
        stage2_used = sum(1 for _, title, _, _ in TEST_CASES if 'youtube' in title.lower() or 'video' in title.lower())
        print(f"Stage 2 applicable: {stage2_used} cases")
        
        return accuracy
        
    except Exception as e:
        print(f"\n⚠️  Error testing new ML: {e}")
        import traceback
        traceback.print_exc()
        return 0


def compare_all():
    """Compare rule-based and two-stage ML approaches."""
    print("\n" + "=" * 80)
    print(" " * 20 + "MODEL COMPARISON")
    print("=" * 80)
    
    rule_acc = test_rule_based()
    test_old_ml()  # Just shows deprecation message
    new_ml_acc = test_new_ml()
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Rule-Based:              {rule_acc:5.1f}%")
    print(f"Two-Stage ML:            {new_ml_acc:5.1f}%")
    print("=" * 80)
    
    if new_ml_acc > rule_acc:
        print("\n🏆 Winner: Two-Stage ML System!")
        improvement = new_ml_acc - rule_acc
        print(f"   Improvement: +{improvement:.1f}% over rule-based")
    elif rule_acc >= new_ml_acc:
        print("\n⚠️  Rule-based is still better. Need more training data!")
    
    print()


if __name__ == "__main__":
    compare_all()
