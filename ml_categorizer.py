"""
Two-Stage ML Classification System
Stage 1: TF-IDF + Logistic Regression (5 categories)
Stage 2: TF-IDF + SVM (Productive vs Entertainment for specific platforms)
"""

import pickle
import re
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.pipeline import Pipeline
import numpy as np

from categorizer import categorize_activity as rule_based_categorize

MODEL_STAGE1_PATH = Path("models/stage1_classifier.pkl")
MODEL_STAGE2_PATH = Path("models/stage2_classifier.pkl")

# Categories for Stage 1
STAGE1_CATEGORIES = ['Productivity', 'Entertainment', 'Social Media', 'Communication', 'Other']

# Categories for Stage 2
STAGE2_CATEGORIES = ['Productive', 'Entertainment']

# Platforms that need Stage 2 classification
STAGE2_PLATFORMS = ['youtube', 'vimeo', 'dailymotion', 'twitch', 'video']


class TwoStageMLCategorizer:
    """Two-stage ML categorizer with Logistic Regression + SVM."""
    
    def __init__(self):
        self.stage1_model = None
        self.stage2_model = None
        self.stage1_trained = False
        self.stage2_trained = False
        self.last_load_time_stage1 = 0.0
        self.last_load_time_stage2 = 0.0
        self.load_models()
    
    def preprocess_text(self, app_name, window_title):
        """
        Clean and combine app name and window title.
        
        Steps:
        1. Lowercase
        2. Remove special characters
        3. Remove extra spaces
        4. Combine app and title
        """
        from categorizer import DataCleaner
        clean_app, clean_title = DataCleaner.clean(app_name, window_title)
        
        combined = f"{clean_app} {clean_title}".lower()
        
        # Remove special characters but keep spaces
        combined = re.sub(r'[^a-z0-9\s]', ' ', combined)
        
        # Remove extra spaces
        combined = ' '.join(combined.split())
        
        return combined
    
    def create_stage1_model(self):
        """
        Create Stage 1 pipeline: TF-IDF + Logistic Regression
        Multi-class classification for 5 categories
        """
        return Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 3),  # Unigrams, bigrams, trigrams
                min_df=2,
                max_df=0.8,
                sublinear_tf=True  # Use log scaling
            )),
            ('classifier', LogisticRegression(
                max_iter=1000,
                multi_class='multinomial',
                solver='lbfgs',
                C=1.0,
                class_weight='balanced'  # Handle imbalanced data
            ))
        ])
    
    def create_stage2_model(self):
        """
        Create Stage 2 pipeline: TF-IDF + SVM
        Binary classification for Productive vs Entertainment
        """
        return Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=800,
                ngram_range=(1, 3),
                min_df=2,
                max_df=0.8,
                sublinear_tf=True
            )),
            ('classifier', SVC(
                kernel='linear',
                C=1.0,
                class_weight='balanced',
                probability=True  # Enable probability estimates
            ))
        ])
    
    def train_stage1(self, training_data):
        """
        Train Stage 1 model on labeled data.
        
        Args:
            training_data: List of tuples [(app_name, window_title, category), ...]
        """
        if len(training_data) < 30:
            print("Stage 1: Not enough training data. Need at least 30 samples.")
            return False
        
        # Prepare data
        X = [self.preprocess_text(app, title) for app, title, _ in training_data]
        y = [category for _, _, category in training_data]
        
        # Create and train model
        self.stage1_model = self.create_stage1_model()
        self.stage1_model.fit(X, y)
        self.stage1_trained = True
        
        print(f"Stage 1 trained on {len(training_data)} samples")
        
        # Show class distribution
        from collections import Counter
        class_dist = Counter(y)
        print("  Class distribution:")
        for cat, count in class_dist.items():
            print(f"    {cat:20} {count:4} samples")
        
        return True
    
    def train_stage2(self, training_data):
        """
        Train Stage 2 model on YouTube/video content.
        
        Args:
            training_data: List of tuples [(app_name, window_title, label), ...]
                          where label is 'Productive' or 'Entertainment'
        """
        if len(training_data) < 20:
            print("Stage 2: Not enough training data. Need at least 20 samples.")
            return False
        
        # Prepare data
        X = [self.preprocess_text(app, title) for app, title, _ in training_data]
        y = [label for _, _, label in training_data]
        
        # Create and train model
        self.stage2_model = self.create_stage2_model()
        self.stage2_model.fit(X, y)
        self.stage2_trained = True
        
        print(f"Stage 2 trained on {len(training_data)} samples")
        
        # Show class distribution
        from collections import Counter
        class_dist = Counter(y)
        print("  Class distribution:")
        for cat, count in class_dist.items():
            print(f"    {cat:20} {count:4} samples")
        
        return True
    
    def check_and_reload(self):
        """Check if model files were modified since last load."""
        import os
        
        # Check Stage 1
        if MODEL_STAGE1_PATH.exists():
            mtime = os.path.getmtime(MODEL_STAGE1_PATH)
            if mtime > self.last_load_time_stage1:
                print("\n[AI UPDATE] Stage 1 model changed. Reloading...")
                self.load_stage1_model()
        
        # Check Stage 2
        if MODEL_STAGE2_PATH.exists():
            mtime = os.path.getmtime(MODEL_STAGE2_PATH)
            if mtime > self.last_load_time_stage2:
                print("\n[AI UPDATE] Stage 2 model changed. Reloading...")
                self.load_stage2_model()
    
    def needs_stage2(self, text):
        """Check if content needs Stage 2 classification."""
        text_lower = text.lower()
        return any(platform in text_lower for platform in STAGE2_PLATFORMS)
    
    def predict(self, app_name, window_title):
        """
        Two-stage prediction.
        
        Stage 1: Classify into 5 categories
        Stage 2: If YouTube/video, further classify as Productive/Entertainment
        
        Args:
            app_name: Application name
            window_title: Window title
            
        Returns:
            str: Final category
        """
        self.check_and_reload()
        
        text = self.preprocess_text(app_name, window_title)
        
        # Handle empty/meaningless text
        if not text.strip() or text.strip() in ["new tab", "untitled", "blank"]:
            return "Other"
        
        # Stage 1: Primary classification
        if not self.stage1_trained or self.stage1_model is None:
            # Fallback to rule-based
            return rule_based_categorize(app_name, window_title)
        
        try:
            stage1_prediction = self.stage1_model.predict([text])[0]
            stage1_probs = self.stage1_model.predict_proba([text])[0]
            stage1_confidence = max(stage1_probs)
            
            # If confidence too low, use rule-based fallback
            if stage1_confidence < 0.4:
                return rule_based_categorize(app_name, window_title)
            
            # Stage 2: Refine if it's video/YouTube content
            if self.needs_stage2(text) and self.stage2_trained and self.stage2_model is not None:
                try:
                    stage2_prediction = self.stage2_model.predict([text])[0]
                    stage2_probs = self.stage2_model.predict_proba([text])[0]
                    stage2_confidence = max(stage2_probs)
                    
                    # Only use Stage 2 if confident
                    if stage2_confidence > 0.5:
                        # Map Stage 2 output back to Stage 1 categories
                        if stage2_prediction == 'Productive':
                            return 'Productivity'
                        else:
                            return 'Entertainment'
                except Exception as e:
                    print(f"Stage 2 prediction failed: {e}")
            
            return stage1_prediction
            
        except Exception as e:
            print(f"ML prediction failed: {e}. Using rule-based fallback.")
            return rule_based_categorize(app_name, window_title)
    
    def save_models(self):
        """Save both trained models to disk."""
        MODEL_STAGE1_PATH.parent.mkdir(exist_ok=True)
        
        if self.stage1_trained and self.stage1_model is not None:
            with open(MODEL_STAGE1_PATH, 'wb') as f:
                pickle.dump(self.stage1_model, f)
            print(f"Stage 1 model saved to {MODEL_STAGE1_PATH}")
        
        if self.stage2_trained and self.stage2_model is not None:
            with open(MODEL_STAGE2_PATH, 'wb') as f:
                pickle.dump(self.stage2_model, f)
            print(f"Stage 2 model saved to {MODEL_STAGE2_PATH}")
        
        return True
    
    def load_models(self):
        """Load both models from disk."""
        self.load_stage1_model()
        self.load_stage2_model()
    
    def load_stage1_model(self):
        """Load Stage 1 model from disk."""
        if MODEL_STAGE1_PATH.exists():
            import os
            try:
                mtime = os.path.getmtime(MODEL_STAGE1_PATH)
                with open(MODEL_STAGE1_PATH, 'rb') as f:
                    self.stage1_model = pickle.load(f)
                self.stage1_trained = True
                self.last_load_time_stage1 = mtime
                print("Stage 1 model loaded successfully")
                return True
            except Exception as e:
                print(f"Failed to load Stage 1 model: {e}")
                return False
        return False
    
    def load_stage2_model(self):
        """Load Stage 2 model from disk."""
        if MODEL_STAGE2_PATH.exists():
            import os
            try:
                mtime = os.path.getmtime(MODEL_STAGE2_PATH)
                with open(MODEL_STAGE2_PATH, 'rb') as f:
                    self.stage2_model = pickle.load(f)
                self.stage2_trained = True
                self.last_load_time_stage2 = mtime
                print("Stage 2 model loaded successfully")
                return True
            except Exception as e:
                print(f"Failed to load Stage 2 model: {e}")
                return False
        return False


# Global instance
_ml_categorizer = None

def get_ml_categorizer():
    """Get or create the global ML categorizer instance."""
    global _ml_categorizer
    if _ml_categorizer is None:
        _ml_categorizer = TwoStageMLCategorizer()
    return _ml_categorizer

def categorize_with_ml(app_name, window_title):
    """
    Categorize activity using two-stage ML (with rule-based fallback).
    
    Args:
        app_name: Application name
        window_title: Window title
        
    Returns:
        str: Category name
    """
    categorizer = get_ml_categorizer()
    return categorizer.predict(app_name, window_title)
