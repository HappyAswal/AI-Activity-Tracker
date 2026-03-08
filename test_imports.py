"""
Quick test to verify all imports work correctly.
"""

print("Testing imports...")

try:
    print("1. Testing categorizer...")
    from categorizer import categorize_activity
    print("   ✓ categorizer OK")
except Exception as e:
    print(f"   ✗ categorizer FAILED: {e}")

try:
    print("2. Testing ml_categorizer...")
    from ml_categorizer import get_ml_categorizer
    print("   ✓ ml_categorizer OK")
except Exception as e:
    print(f"   ✗ ml_categorizer FAILED: {e}")

try:
    print("3. Testing train_model...")
    from train_model import train_two_stage_model
    print("   ✓ train_model OK")
except Exception as e:
    print(f"   ✗ train_model FAILED: {e}")

try:
    print("4. Testing sklearn...")
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC
    print("   ✓ sklearn OK")
except Exception as e:
    print(f"   ✗ sklearn FAILED: {e}")

try:
    print("5. Testing database...")
    from database import init_database
    print("   ✓ database OK")
except Exception as e:
    print(f"   ✗ database FAILED: {e}")

print("\n" + "="*50)
print("All imports successful! ✓")
print("="*50)
