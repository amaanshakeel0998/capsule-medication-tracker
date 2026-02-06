# database/db_manager.py
# Database manager for medication tracking system

import sqlite3
from datetime import datetime, timedelta
import config

class DatabaseManager:
    """Manages all database operations for medication tracking"""
    
    def __init__(self):
        self.db_path = config.DATABASE_PATH
        self.initialize_database()
    
    def get_connection(self):
        """Create and return database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        return conn
    
    def initialize_database(self):
        """Create tables if they don't exist"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Medications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                dosage TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Schedules table (multiple times per day allowed)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medication_id INTEGER NOT NULL,
                scheduled_time TEXT NOT NULL,
                FOREIGN KEY (medication_id) REFERENCES medications (id)
            )
        ''')
        
        # Dose history table (tracks taken, missed, delayed)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dose_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medication_id INTEGER NOT NULL,
                scheduled_time TIMESTAMP NOT NULL,
                actual_time TIMESTAMP,
                status TEXT NOT NULL,
                delay_minutes INTEGER DEFAULT 0,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (medication_id) REFERENCES medications (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_medication(self, name, dosage, schedule_times):
        """
        Add new medication with schedule
        schedule_times: list of times like ['08:00', '14:00', '20:00']
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Insert medication
        cursor.execute(
            'INSERT INTO medications (name, dosage) VALUES (?, ?)',
            (name, dosage)
        )
        medication_id = cursor.lastrowid
        
        # Insert schedules
        for time in schedule_times:
            cursor.execute(
                'INSERT INTO schedules (medication_id, scheduled_time) VALUES (?, ?)',
                (medication_id, time)
            )
        
        conn.commit()
        conn.close()
        return medication_id
    
    def get_medication_by_id(self, medication_id):
        """Get single medication with schedules by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM medications WHERE id = ?', (medication_id,))
        med = cursor.fetchone()
        
        if not med:
            conn.close()
            return None
        
        cursor.execute(
            'SELECT scheduled_time FROM schedules WHERE medication_id = ?',
            (medication_id,)
        )
        schedules = [row['scheduled_time'] for row in cursor.fetchall()]
        
        result = {
            'id': med['id'],
            'name': med['name'],
            'dosage': med['dosage'],
            'schedules': schedules,
            'created_at': med['created_at']
        }
        
        conn.close()
        return result
    
    def update_medication(self, medication_id, name, dosage, schedule_times):
        """
        Update existing medication and its schedules
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Update medication info
        cursor.execute(
            'UPDATE medications SET name = ?, dosage = ? WHERE id = ?',
            (name, dosage, medication_id)
        )
        
        # Delete old schedules
        cursor.execute(
            'DELETE FROM schedules WHERE medication_id = ?',
            (medication_id,)
        )
        
        # Insert new schedules
        for time in schedule_times:
            cursor.execute(
                'INSERT INTO schedules (medication_id, scheduled_time) VALUES (?, ?)',
                (medication_id, time)
            )
        
        conn.commit()
        conn.close()
        return True
    
    def delete_medication(self, medication_id):
        """
        Delete medication and all related data
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Delete schedules
        cursor.execute(
            'DELETE FROM schedules WHERE medication_id = ?',
            (medication_id,)
        )
        
        # Delete dose history
        cursor.execute(
            'DELETE FROM dose_history WHERE medication_id = ?',
            (medication_id,)
        )
        
        # Delete medication
        cursor.execute(
            'DELETE FROM medications WHERE id = ?',
            (medication_id,)
        )
        
        conn.commit()
        conn.close()
        return True
    
    def get_all_medications(self):
        """Get all medications with their schedules"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM medications')
        medications = cursor.fetchall()
        
        result = []
        for med in medications:
            cursor.execute(
                'SELECT scheduled_time FROM schedules WHERE medication_id = ?',
                (med['id'],)
            )
            schedules = [row['scheduled_time'] for row in cursor.fetchall()]
            
            result.append({
                'id': med['id'],
                'name': med['name'],
                'dosage': med['dosage'],
                'schedules': schedules,
                'created_at': med['created_at']
            })
        
        conn.close()
        return result
    
    def record_dose(self, medication_id, scheduled_time, actual_time, status):
        """
        Record a dose taken/missed/delayed
        status: 'taken', 'missed', 'delayed'
        
        FIXED: Only mark as delayed if explicitly more than DELAY_TOLERANCE
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Calculate delay if taken
        delay_minutes = 0
        
        if status == 'taken' and actual_time:
            try:
                scheduled_dt = datetime.strptime(scheduled_time, '%Y-%m-%d %H:%M')
                actual_dt = datetime.strptime(actual_time, '%Y-%m-%d %H:%M')
                delay_minutes = int((actual_dt - scheduled_dt).total_seconds() / 60)
                
                # FIXED: Only change to delayed if SIGNIFICANTLY late
                # Positive delay = taken late, Negative = taken early
                if delay_minutes > config.DELAY_TOLERANCE:
                    status = 'delayed'
                else:
                    # If within tolerance or early, keep as "taken"
                    status = 'taken'
                    
            except Exception as e:
                print(f"Error calculating delay: {e}")
                # If error in calculation, keep original status
                pass
        
        cursor.execute('''
            INSERT INTO dose_history 
            (medication_id, scheduled_time, actual_time, status, delay_minutes)
            VALUES (?, ?, ?, ?, ?)
        ''', (medication_id, scheduled_time, actual_time, status, delay_minutes))
        
        conn.commit()
        conn.close()
    
    def get_dose_history(self, days=30):
        """Get dose history for last N days"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT dh.*, m.name, m.dosage
            FROM dose_history dh
            JOIN medications m ON dh.medication_id = m.id
            WHERE dh.scheduled_time >= ?
            ORDER BY dh.scheduled_time DESC
        ''', (start_date,))
        
        history = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in history]
    
    def get_todays_schedule(self):
        """Get today's medication schedule"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT m.id, m.name, m.dosage, s.scheduled_time
            FROM medications m
            JOIN schedules s ON m.id = s.medication_id
        ''')
        
        schedules = cursor.fetchall()
        conn.close()
        
        # Add today's date to scheduled times
        result = []
        for schedule in schedules:
            result.append({
                'medication_id': schedule['id'],
                'name': schedule['name'],
                'dosage': schedule['dosage'],
                'scheduled_time': f"{today} {schedule['scheduled_time']}"
            })
        
        return result
    
    def get_statistics(self):
        """Get overall statistics for dashboard"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total medications
        cursor.execute('SELECT COUNT(*) as count FROM medications')
        total_meds = cursor.fetchone()['count']
        
        # This week's stats
        week_start = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM dose_history
            WHERE scheduled_time >= ?
            GROUP BY status
        ''', (week_start,))
        
        stats = cursor.fetchall()
        conn.close()
        
        # Format stats
        taken = 0
        missed = 0
        delayed = 0
        
        for stat in stats:
            if stat['status'] == 'taken':
                taken = stat['count']
            elif stat['status'] == 'missed':
                missed = stat['count']
            elif stat['status'] == 'delayed':
                delayed = stat['count']
        
        return {
            'total_medications': total_meds,
            'taken_this_week': taken,
            'missed_this_week': missed,
            'delayed_this_week': delayed,
            'total_doses_this_week': taken + missed + delayed
        }