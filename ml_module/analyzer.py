# ml_module/analyzer.py
# Behavior analysis module for medication tracking

from datetime import datetime, timedelta
import config

class BehaviorAnalyzer:
    """Analyzes medication adherence patterns"""
    
    def __init__(self, db_manager):
        self.db = db_manager
    
    def analyze_adherence_rate(self, days=30):
        """Calculate adherence rate for last N days"""
        history = self.db.get_dose_history(days=days)
        
        if not history:
            return {
                'adherence_rate': 0,
                'total_doses': 0,
                'taken': 0,
                'missed': 0,
                'delayed': 0
            }
        
        taken = sum(1 for h in history if h['status'] == 'taken')
        missed = sum(1 for h in history if h['status'] == 'missed')
        delayed = sum(1 for h in history if h['status'] == 'delayed')
        total = len(history)
        
        # Adherence rate = (taken + delayed) / total
        adherence_rate = ((taken + delayed) / total * 100) if total > 0 else 0
        
        return {
            'adherence_rate': round(adherence_rate, 2),
            'total_doses': total,
            'taken': taken,
            'missed': missed,
            'delayed': delayed
        }
    
    def detect_patterns(self, medication_id=None):
        """Detect patterns in medication taking behavior"""
        history = self.db.get_dose_history(days=30)
        
        # Filter by medication if specified
        if medication_id:
            history = [h for h in history if h['medication_id'] == medication_id]
        
        if not history:
            return {'patterns': []}
        
        patterns = []
        
        # Pattern 1: Frequent weekend misses
        weekend_misses = 0
        weekday_misses = 0
        
        for record in history:
            if record['status'] == 'missed':
                dose_date = datetime.strptime(record['scheduled_time'], '%Y-%m-%d %H:%M')
                if dose_date.weekday() >= 5:  # Saturday=5, Sunday=6
                    weekend_misses += 1
                else:
                    weekday_misses += 1
        
        if weekend_misses > weekday_misses * 1.5:
            patterns.append({
                'type': 'weekend_misses',
                'description': 'You tend to miss doses on weekends',
                'severity': 'medium'
            })
        
        # Pattern 2: Consistent delays
        delays = [h['delay_minutes'] for h in history if h['status'] == 'delayed']
        if len(delays) > 5:
            avg_delay = sum(delays) / len(delays)
            if avg_delay > 60:
                patterns.append({
                    'type': 'consistent_delays',
                    'description': f'Average delay is {int(avg_delay)} minutes',
                    'severity': 'medium'
                })
        
        # Pattern 3: Specific time slot issues
        time_slot_misses = {}
        for record in history:
            if record['status'] == 'missed':
                time = datetime.strptime(record['scheduled_time'], '%Y-%m-%d %H:%M').hour
                time_slot_misses[time] = time_slot_misses.get(time, 0) + 1
        
        if time_slot_misses:
            worst_time = max(time_slot_misses, key=time_slot_misses.get)
            if time_slot_misses[worst_time] >= 3:
                patterns.append({
                    'type': 'time_slot_issue',
                    'description': f'Most misses occur around {worst_time}:00',
                    'severity': 'high'
                })
        
        # Pattern 4: Improving or declining trend
        recent_adherence = self.analyze_adherence_rate(days=7)['adherence_rate']
        older_adherence = self.analyze_adherence_rate(days=30)['adherence_rate']
        
        if recent_adherence > older_adherence + 10:
            patterns.append({
                'type': 'improving',
                'description': 'Your adherence is improving!',
                'severity': 'positive'
            })
        elif recent_adherence < older_adherence - 10:
            patterns.append({
                'type': 'declining',
                'description': 'Your adherence is declining',
                'severity': 'high'
            })
        
        return {'patterns': patterns}
    
    def get_risk_factors(self, medication_id):
        """Identify risk factors for missing next dose"""
        history = self.db.get_dose_history(days=14)
        history = [h for h in history if h['medication_id'] == medication_id]
        
        if len(history) < 5:
            return {
                'risk_level': 'unknown',
                'factors': ['Not enough data to predict']
            }
        
        factors = []
        
        # Recent misses
        recent_misses = sum(1 for h in history[:7] if h['status'] == 'missed')
        if recent_misses >= 2:
            factors.append(f'Missed {recent_misses} doses in last week')
        
        # Delay trend
        recent_delays = [h['delay_minutes'] for h in history[:7] if h['status'] == 'delayed']
        if len(recent_delays) >= 3:
            factors.append('Frequent delays recently')
        
        # Calculate risk level
        miss_rate = recent_misses / 7 if len(history) >= 7 else 0
        
        if miss_rate > 0.3:
            risk_level = 'high'
        elif miss_rate > 0.1:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return {
            'risk_level': risk_level,
            'factors': factors if factors else ['Good adherence pattern']
        }
    
    def generate_insights(self):
        """Generate overall insights for user"""
        adherence = self.analyze_adherence_rate(days=30)
        patterns = self.detect_patterns()
        
        insights = []
        
        # Adherence insight
        if adherence['adherence_rate'] >= 90:
            insights.append({
                'type': 'success',
                'message': f"Excellent adherence! {adherence['adherence_rate']}% on track"
            })
        elif adherence['adherence_rate'] >= 70:
            insights.append({
                'type': 'warning',
                'message': f"Good adherence at {adherence['adherence_rate']}%, but room for improvement"
            })
        else:
            insights.append({
                'type': 'alert',
                'message': f"Low adherence at {adherence['adherence_rate']}%. Please improve consistency"
            })
        
        # Pattern insights
        for pattern in patterns['patterns']:
            insights.append({
                'type': 'info',
                'message': pattern['description']
            })
        
        return insights