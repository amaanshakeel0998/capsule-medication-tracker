# ml_module/predictor.py
# Machine Learning predictor for missed dose probability

from datetime import datetime, timedelta
import pickle
import os
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import numpy as np
import config

class MissedDosePredictor:
    """Predicts probability of missing next dose using ML"""
    
    def __init__(self, db_manager):
        self.db = db_manager
        self.model = None
        self.scaler = StandardScaler()
        self.load_model()
    
    def load_model(self):
        """Load trained model if exists"""
        if os.path.exists(config.MODEL_PATH):
            try:
                with open(config.MODEL_PATH, 'rb') as f:
                    saved_data = pickle.load(f)
                    self.model = saved_data['model']
                    self.scaler = saved_data['scaler']
            except:
                self.model = None
    
    def save_model(self):
        """Save trained model"""
        os.makedirs(os.path.dirname(config.MODEL_PATH), exist_ok=True)
        with open(config.MODEL_PATH, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'scaler': self.scaler
            }, f)
    
    def extract_features(self, history, target_time):
        """
        Extract features for ML model
        Features:
        1. Hour of day
        2. Day of week (0=Monday, 6=Sunday)
        3. Recent miss rate (last 7 days)
        4. Average delay (last 7 days)
        5. Streak of consecutive takes
        """
        target_dt = datetime.strptime(target_time, '%Y-%m-%d %H:%M')
        
        # Feature 1: Hour of day
        hour = target_dt.hour
        
        # Feature 2: Day of week
        day_of_week = target_dt.weekday()
        
        # Feature 3: Recent miss rate
        recent_history = [h for h in history if 
                         datetime.strptime(h['scheduled_time'], '%Y-%m-%d %H:%M') 
                         > target_dt - timedelta(days=7)]
        
        if recent_history:
            miss_rate = sum(1 for h in recent_history if h['status'] == 'missed') / len(recent_history)
        else:
            miss_rate = 0
        
        # Feature 4: Average delay
        delays = [h['delay_minutes'] for h in recent_history if h['status'] == 'delayed']
        avg_delay = sum(delays) / len(delays) if delays else 0
        
        # Feature 5: Current streak
        streak = 0
        sorted_history = sorted(history, 
                               key=lambda x: x['scheduled_time'], 
                               reverse=True)
        
        for record in sorted_history:
            if record['status'] in ['taken', 'delayed']:
                streak += 1
            else:
                break
        
        return [hour, day_of_week, miss_rate, avg_delay, streak]
    
    def train_model(self):
        """Train the ML model using historical data"""
        history = self.db.get_dose_history(days=60)
        
        if len(history) < config.TRAINING_DATA_MIN_RECORDS:
            return False
        
        X = []  # Features
        y = []  # Labels (1=missed, 0=taken/delayed)
        
        # Create training data
        for i, record in enumerate(history):
            # Use history before this record
            past_history = history[i+1:]
            
            if len(past_history) >= 3:  # Need some history
                features = self.extract_features(past_history, record['scheduled_time'])
                X.append(features)
                
                # Label: 1 if missed, 0 otherwise
                label = 1 if record['status'] == 'missed' else 0
                y.append(label)
        
        if len(X) < config.TRAINING_DATA_MIN_RECORDS:
            return False
        
        # Train model
        X = np.array(X)
        y = np.array(y)
        
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train Logistic Regression
        self.model = LogisticRegression(random_state=42, max_iter=1000)
        self.model.fit(X_scaled, y)
        
        # Save model
        self.save_model()
        
        return True
    
    def predict_miss_probability(self, medication_id, scheduled_time):
        """
        Predict probability of missing a dose
        Returns: probability (0-1)
        """
        # Get history for this medication
        all_history = self.db.get_dose_history(days=30)
        history = [h for h in all_history if h['medication_id'] == medication_id]
        
        # Need minimum data
        if len(history) < 5:
            return {
                'probability': 0.0,
                'risk_level': 'unknown',
                'message': 'Not enough data to predict'
            }
        
        # Train model if not exists
        if self.model is None:
            trained = self.train_model()
            if not trained:
                return {
                    'probability': 0.0,
                    'risk_level': 'unknown',
                    'message': 'Insufficient data to train model'
                }
        
        # Extract features
        features = self.extract_features(history, scheduled_time)
        features_scaled = self.scaler.transform([features])
        
        # Predict
        probability = self.model.predict_proba(features_scaled)[0][1]
        
        # Determine risk level
        if probability > config.MISS_PROBABILITY_THRESHOLD:
            risk_level = 'high'
            message = f'High risk of missing dose ({int(probability*100)}% probability)'
        elif probability > 0.3:
            risk_level = 'medium'
            message = f'Medium risk ({int(probability*100)}% probability)'
        else:
            risk_level = 'low'
            message = f'Low risk ({int(probability*100)}% probability)'
        
        return {
            'probability': round(probability, 3),
            'risk_level': risk_level,
            'message': message
        }
    
    def get_predictions_for_today(self):
        """Get predictions for all today's scheduled doses"""
        schedule = self.db.get_todays_schedule()
        predictions = []
        
        for dose in schedule:
            prediction = self.predict_miss_probability(
                dose['medication_id'], 
                dose['scheduled_time']
            )
            
            predictions.append({
                'medication_name': dose['name'],
                'scheduled_time': dose['scheduled_time'],
                'prediction': prediction
            })
        
        return predictions