# app.py
# Main Flask application for Capsule Medication Tracker

from flask import Flask, render_template, request, jsonify
from datetime import datetime, timedelta
import config
from database.db_manager import DatabaseManager
from ml_module.predictor import MissedDosePredictor
from ml_module.analyzer import BehaviorAnalyzer

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

# Initialize database
db = DatabaseManager()

# Initialize ML modules
predictor = MissedDosePredictor(db)
analyzer = BehaviorAnalyzer(db)

# ============================================
# ROUTES - Web Pages
# ============================================

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/add-medication')
def add_medication_page():
    """Page to add new medication"""
    return render_template('add_medication.html')

@app.route('/edit-medication/<int:medication_id>')
def edit_medication_page(medication_id):
    """Page to edit existing medication"""
    return render_template('edit_medication.html', medication_id=medication_id)

@app.route('/schedule')
def schedule_page():
    """View schedule page"""
    return render_template('schedule.html')

@app.route('/reports')
def reports_page():
    """Reports and statistics page"""
    return render_template('reports.html')

@app.route('/ai-insights')
def ai_insights_page():
    """AI predictions and insights page"""
    return render_template('ai_insights.html')

# ============================================
# API ROUTES - Data Operations
# ============================================

@app.route('/api/medications', methods=['GET'])
def get_medications():
    """Get all medications"""
    medications = db.get_all_medications()
    return jsonify({'success': True, 'data': medications})

@app.route('/api/medications/<int:medication_id>', methods=['GET'])
def get_medication(medication_id):
    """Get single medication by ID"""
    medication = db.get_medication_by_id(medication_id)
    
    if medication:
        return jsonify({'success': True, 'data': medication})
    else:
        return jsonify({'success': False, 'message': 'Medication not found'}), 404

@app.route('/api/medications', methods=['POST'])
def add_medication():
    """Add new medication"""
    data = request.json
    
    name = data.get('name')
    dosage = data.get('dosage')
    schedules = data.get('schedules', [])
    
    if not name or not dosage or not schedules:
        return jsonify({'success': False, 'message': 'Missing required fields'})
    
    med_id = db.add_medication(name, dosage, schedules)
    
    return jsonify({
        'success': True, 
        'message': 'Medication added successfully',
        'medication_id': med_id
    })

@app.route('/api/medications/<int:medication_id>', methods=['PUT'])
def update_medication(medication_id):
    """Update existing medication"""
    data = request.json
    
    name = data.get('name')
    dosage = data.get('dosage')
    schedules = data.get('schedules', [])
    
    if not name or not dosage or not schedules:
        return jsonify({'success': False, 'message': 'Missing required fields'})
    
    # Check if medication exists
    existing = db.get_medication_by_id(medication_id)
    if not existing:
        return jsonify({'success': False, 'message': 'Medication not found'}), 404
    
    success = db.update_medication(medication_id, name, dosage, schedules)
    
    if success:
        return jsonify({'success': True, 'message': 'Medication updated successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to update medication'})

@app.route('/api/medications/<int:medication_id>', methods=['DELETE'])
def delete_medication(medication_id):
    """Delete medication"""
    # Check if medication exists
    existing = db.get_medication_by_id(medication_id)
    if not existing:
        return jsonify({'success': False, 'message': 'Medication not found'}), 404
    
    success = db.delete_medication(medication_id)
    
    if success:
        return jsonify({'success': True, 'message': 'Medication deleted successfully'})
    else:
        return jsonify({'success': False, 'message': 'Failed to delete medication'})

@app.route('/api/record-dose', methods=['POST'])
def record_dose():
    """Record a dose as taken/missed/delayed"""
    data = request.json
    
    medication_id = data.get('medication_id')
    scheduled_time = data.get('scheduled_time')
    actual_time = data.get('actual_time')
    status = data.get('status')  # 'taken', 'missed', 'delayed'
    
    if not all([medication_id, scheduled_time, status]):
        return jsonify({'success': False, 'message': 'Missing required fields'})
    
    db.record_dose(medication_id, scheduled_time, actual_time, status)
    
    return jsonify({'success': True, 'message': 'Dose recorded successfully'})

@app.route('/api/todays-schedule', methods=['GET'])
def get_todays_schedule():
    """Get today's medication schedule"""
    schedule = db.get_todays_schedule()
    return jsonify({'success': True, 'data': schedule})

@app.route('/api/dose-history', methods=['GET'])
def get_dose_history():
    """Get dose history"""
    days = request.args.get('days', 30, type=int)
    history = db.get_dose_history(days=days)
    return jsonify({'success': True, 'data': history})

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """Get overall statistics"""
    stats = db.get_statistics()
    return jsonify({'success': True, 'data': stats})

# ============================================
# AI/ML API ROUTES
# ============================================

@app.route('/api/ai/predictions', methods=['GET'])
def get_predictions():
    """Get AI predictions for today"""
    predictions = predictor.get_predictions_for_today()
    return jsonify({'success': True, 'data': predictions})

@app.route('/api/ai/predict-dose', methods=['POST'])
def predict_single_dose():
    """Predict probability for a specific dose"""
    data = request.json
    
    medication_id = data.get('medication_id')
    scheduled_time = data.get('scheduled_time')
    
    if not medication_id or not scheduled_time:
        return jsonify({'success': False, 'message': 'Missing required fields'})
    
    prediction = predictor.predict_miss_probability(medication_id, scheduled_time)
    
    return jsonify({'success': True, 'data': prediction})

@app.route('/api/ai/analyze-adherence', methods=['GET'])
def analyze_adherence():
    """Get adherence analysis"""
    days = request.args.get('days', 30, type=int)
    analysis = analyzer.analyze_adherence_rate(days=days)
    return jsonify({'success': True, 'data': analysis})

@app.route('/api/ai/detect-patterns', methods=['GET'])
def detect_patterns():
    """Detect behavioral patterns"""
    medication_id = request.args.get('medication_id', type=int)
    patterns = analyzer.detect_patterns(medication_id=medication_id)
    return jsonify({'success': True, 'data': patterns})

@app.route('/api/ai/insights', methods=['GET'])
def get_insights():
    """Get overall AI insights"""
    insights = analyzer.generate_insights()
    return jsonify({'success': True, 'data': insights})

@app.route('/api/ai/train-model', methods=['POST'])
def train_model():
    """Manually trigger model training"""
    success = predictor.train_model()
    
    if success:
        return jsonify({'success': True, 'message': 'Model trained successfully'})
    else:
        return jsonify({'success': False, 'message': 'Not enough data to train model'})

# ============================================
# ERROR HANDLERS
# ============================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'message': 'Route not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'message': 'Internal server error'}), 500

# ============================================
# RUN APPLICATION
# ============================================

if __name__ == '__main__':
    print("=" * 60)
    print("🏥 CAPSULE MEDICATION TRACKER")
    print("=" * 60)
    print("Starting server...")
    print(f"Dashboard: http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=config.DEBUG_MODE, host='0.0.0.0', port=5000)