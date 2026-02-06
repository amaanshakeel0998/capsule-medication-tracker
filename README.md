# 💊 Capsule Medication Tracker Using AI

## 📋 Project Overview

A professional web-based medication tracking system that uses **Artificial Intelligence (Machine Learning)** to predict missed doses and analyze user behavior patterns. Built as a semester project for Artificial Intelligence course.

---

## 🎯 Project Objectives

1. **Medication Management**: Track multiple medications with custom schedules
2. **Smart Reminders**: Browser notifications and audio alerts
3. **AI Predictions**: Predict likelihood of missing doses using ML
4. **Behavior Analysis**: Detect patterns in medication adherence
5. **Comprehensive Reporting**: Visual reports and statistics

---

## 🤖 AI/ML Implementation

### **Machine Learning Algorithm Used**

**Logistic Regression** (scikit-learn)

### **Why Logistic Regression?**

- Simple and explainable (perfect for beginners)
- Binary classification (will miss dose: Yes/No)
- Provides probability scores (0-1 range)
- Trains quickly with limited data
- Industry-standard for healthcare predictions

### **Features Used for Prediction**

The ML model analyzes 5 key features:

1. **Hour of Day**: What time the dose is scheduled
2. **Day of Week**: Monday through Sunday (0-6)
3. **Recent Miss Rate**: Percentage of doses missed in last 7 days
4. **Average Delay**: How late doses are typically taken
5. **Current Streak**: Consecutive successful doses

### **How It Works**
```
User History → Feature Extraction → ML Model → Probability Score → Risk Level
```

**Example:**
- If you frequently miss evening doses on weekends, the AI will flag your Saturday 8 PM dose as "high risk"
- The system provides probability (e.g., 75% chance of missing)
- Risk levels: LOW (<30%), MEDIUM (30-60%), HIGH (>60%)

---

## 🏗️ Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Python Flask |
| **Database** | SQLite |
| **Frontend** | HTML5, CSS3, JavaScript |
| **ML Library** | scikit-learn |
| **Data Processing** | pandas, numpy |

---

## 📁 Project Structure
```
capsule-medication-tracker/
│
├── app.py                      # Main Flask application
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── database/
│   ├── db_manager.py          # Database operations
│   └── medication_tracker.db  # SQLite database (auto-created)
│
├── ml_module/
│   ├── predictor.py           # AI prediction engine
│   ├── analyzer.py            # Behavior analysis
│   └── model_trainer.py       # Model training script
│
├── static/
│   ├── css/
│   │   └── style.css          # Professional styling
│   ├── js/
│   │   ├── main.js            # Core functionality
│   │   ├── notifications.js   # Browser notifications
│   │   └── reports.js         # Report generation
│   └── sounds/
│       └── alarm.mp3          # Reminder sound
│
└── templates/
    ├── index.html             # Dashboard
    ├── add_medication.html    # Add medication form
    ├── schedule.html          # Schedule view
    ├── reports.html           # Reports & analytics
    └── ai_insights.html       # AI predictions page
```

---

## 🚀 How to Run

### **Prerequisites**

- Python 3.8 or higher
- pip (Python package manager)

### **Installation Steps**

1. **Extract the project folder**

2. **Open terminal/command prompt in project directory**

3. **Install dependencies:**
```bash
   pip install -r requirements.txt
```

4. **Run the application:**
```bash
   python app.py
```

5. **Open browser and visit:**
```
   http://localhost:5000
```

---

## 📖 How to Use

### **Step 1: Add Medications**

1. Click "Add Medication" in navigation
2. Enter medication name (e.g., "Aspirin")
3. Enter dosage (e.g., "500mg")
4. Add schedule times (e.g., 8:00 AM, 2:00 PM, 8:00 PM)
5. Click "Add Medication"

### **Step 2: Track Daily Doses**

1. Dashboard shows today's schedule
2. Mark each dose as "Taken" or "Missed"
3. System records time and calculates delays

### **Step 3: View AI Insights**

1. Navigate to "AI Insights"
2. See predictions for today's doses
3. View detected behavior patterns
4. Check personalized recommendations

### **Step 4: Review Reports**

1. Go to "Reports" page
2. View adherence rate (percentage)
3. See weekly trends (charts)
4. Check dose history table

---

## 🧠 AI Model Training

The AI model automatically trains when you have at least **10 historical records**.

### **Manual Training:**

1. Go to "AI Insights" page
2. Click "Retrain AI Model" button
3. System will update predictions

### **What Happens During Training:**

1. Fetches last 60 days of history
2. Extracts features from each dose
3. Trains Logistic Regression model
4. Saves model for future predictions

---

## 📊 Features Explained

### **1. Dashboard**
- Quick overview of statistics
- Today's medication schedule
- One-click dose marking

### **2. Smart Reminders**
- Browser notifications 15 minutes before dose
- On-screen alerts at exact time
- Audio alarm (if enabled)

### **3. AI Predictions**
- Predicts probability of missing each dose
- Color-coded risk levels (green/yellow/red)
- Explains reasoning behind predictions

### **4. Behavior Analysis**
- Detects weekend vs weekday patterns
- Identifies problematic time slots
- Tracks improvement/decline trends

### **5. Reports**
- Adherence rate calculation
- Pie chart visualization
- Weekly trend bar chart
- Complete dose history table

---

## 🎓 For Viva/Presentation

### **Key Points to Explain:**

1. **Why AI?**
   - Healthcare requires predictive systems
   - Helps users improve adherence
   - Reduces medication errors

2. **ML Algorithm Choice:**
   - Logistic Regression is simple and effective
   - Provides interpretable results
   - Suitable for binary classification

3. **Real-World Application:**
   - 50% of patients don't take medications correctly
   - AI can improve health outcomes
   - Reduces hospital readmissions

4. **Technical Implementation:**
   - Flask backend for API endpoints
   - SQLite for lightweight database
   - scikit-learn for ML operations
   - Vanilla JavaScript for frontend

---

## 🔮 Future Enhancements

1. **User Authentication**: Multi-user support with login
2. **Mobile App**: Native iOS/Android applications
3. **Advanced ML**: Deep learning for better predictions
4. **Doctor Integration**: Share reports with healthcare providers
5. **Medication Interactions**: Check for drug conflicts
6. **SMS Reminders**: Text message notifications
7. **Family Sharing**: Track medications for dependents
8. **Prescription Scanning**: OCR to auto-add medications

---

## 🐛 Troubleshooting

### **Database Errors:**
- Delete `medication_tracker.db` and restart the app
- Database will be recreated automatically

### **ML Model Not Training:**
- You need at least 10 dose records
- Add more medications and track them for a few days

### **Notifications Not Working:**
- Allow notifications in browser settings
- Check if browser supports Notification API

### **Port Already in Use:**
- Change port in `app.py`: `app.run(port=5001)`

---

## 👨‍💻 Developer Information

**Project Type**: Artificial Intelligence Semester Project
**Developer Name**: Muhammad Amaan
**Difficulty Level**: Beginner-Friendly  
**Estimated Completion Time**: 4-6 weeks  
**Lines of Code**: ~1500  

---

## 📝 License

This is an educational project for academic purposes.

---

## 🙏 Acknowledgments

- scikit-learn documentation
- Flask documentation
- Healthcare AI research papers

---

## 📧 Support

For questions or issues, please create an issue in the project repository or contact your course instructor.

---

**Built with ❤️ for AI Education**
