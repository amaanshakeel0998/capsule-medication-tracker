# config.py
# Configuration file for Capsule Medication Tracker

import os

# Base directory of the project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Database configuration
DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'medication_tracker.db')

# ML Model configuration
MODEL_PATH = os.path.join(BASE_DIR, 'ml_module', 'missed_dose_model.pkl')
TRAINING_DATA_MIN_RECORDS = 10  # Minimum records needed to train ML model

# Reminder settings
REMINDER_CHECK_INTERVAL = 60  # Check for reminders every 60 seconds
EARLY_REMINDER_MINUTES = 15  # Remind 15 minutes before scheduled time

# Delay tolerance (in minutes)
# FIXED: Increased from 30 to 60 minutes for better user experience
# If taken within 60 minutes of scheduled time, considered "on time"
DELAY_TOLERANCE = 60

# AI prediction thresholds
MISS_PROBABILITY_THRESHOLD = 0.6  # Above 60% = high risk of missing dose

# Application settings
SECRET_KEY = 'your-secret-key-change-in-production'
DEBUG_MODE = True