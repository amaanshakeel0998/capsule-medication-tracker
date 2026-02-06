# ml_module/model_trainer.py
# Script to train or retrain the ML model

import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db_manager import DatabaseManager
from ml_module.predictor import MissedDosePredictor

def train_model():
    """Train the missed dose prediction model"""
    print("=" * 50)
    print("ML MODEL TRAINER")
    print("=" * 50)
    
    # Initialize database
    db = DatabaseManager()
    
    # Initialize predictor
    predictor = MissedDosePredictor(db)
    
    print("\nFetching historical data...")
    history = db.get_dose_history(days=60)
    print(f"Found {len(history)} historical records")
    
    if len(history) < 10:
        print("\n❌ Not enough data to train model")
        print("Need at least 10 historical records")
        print("Please use the app and record more doses")
        return False
    
    print("\nTraining model...")
    success = predictor.train_model()
    
    if success:
        print("✅ Model trained successfully!")
        print(f"Model saved to: {predictor.model}")
    else:
        print("❌ Training failed")
    
    return success

if __name__ == "__main__":
    train_model()