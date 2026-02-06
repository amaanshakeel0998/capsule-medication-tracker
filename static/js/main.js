// static/js/main.js
// Main JavaScript for Capsule Medication Tracker

// ============================================
// GLOBAL VARIABLES
// ============================================

let allMedications = [];
let todaysSchedule = [];

// ============================================
// UTILITY FUNCTIONS
// ============================================

/**
 * Format date to readable string
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Format time from 24hr to 12hr
 */
function formatTime(timeString) {
    const [hours, minutes] = timeString.split(':');
    const hour = parseInt(hours);
    const ampm = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour % 12 || 12;
    return `${displayHour}:${minutes} ${ampm}`;
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    const container = document.querySelector('.main-content');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

/**
 * Make API request
 */
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        return data;
        
    } catch (error) {
        console.error('API Error:', error);
        showAlert('An error occurred. Please try again.', 'error');
        return null;
    }
}

// ============================================
// MEDICATION FUNCTIONS
// ============================================

/**
 * Load all medications
 */
async function loadMedications() {
    const result = await apiRequest('/api/medications');
    
    if (result && result.success) {
        allMedications = result.data;
        return allMedications;
    }
    
    return [];
}

/**
 * Add new medication
 */
async function addMedication(name, dosage, schedules) {
    const result = await apiRequest('/api/medications', {
        method: 'POST',
        body: JSON.stringify({
            name: name,
            dosage: dosage,
            schedules: schedules
        })
    });
    
    if (result && result.success) {
        showAlert('Medication added successfully!', 'success');
        return true;
    }
    
    showAlert('Failed to add medication', 'error');
    return false;
}

/**
 * Load today's schedule
 */
async function loadTodaysSchedule() {
    const result = await apiRequest('/api/todays-schedule');
    
    if (result && result.success) {
        todaysSchedule = result.data;
        return todaysSchedule;
    }
    
    return [];
}

/**
 * Record a dose
 */
async function recordDose(medicationId, scheduledTime, status) {
    const actualTime = status === 'taken' ? new Date().toISOString().slice(0, 16).replace('T', ' ') : null;
    
    const result = await apiRequest('/api/record-dose', {
        method: 'POST',
        body: JSON.stringify({
            medication_id: medicationId,
            scheduled_time: scheduledTime,
            actual_time: actualTime,
            status: status
        })
    });
    
    if (result && result.success) {
        showAlert(`Dose marked as ${status}!`, 'success');
        
        // Request notification permission if taken
        if (status === 'taken' && 'Notification' in window) {
            Notification.requestPermission();
        }
        
        return true;
    }
    
    return false;
}

// ============================================
// STATISTICS FUNCTIONS
// ============================================

/**
 * Load statistics
 */
async function loadStatistics() {
    const result = await apiRequest('/api/statistics');
    
    if (result && result.success) {
        return result.data;
    }
    
    return null;
}

/**
 * Display statistics on dashboard
 */
async function displayStatistics() {
    const stats = await loadStatistics();
    
    if (!stats) return;
    
    document.getElementById('total-medications').textContent = stats.total_medications || 0;
    document.getElementById('taken-week').textContent = stats.taken_this_week || 0;
    document.getElementById('missed-week').textContent = stats.missed_this_week || 0;
    document.getElementById('delayed-week').textContent = stats.delayed_this_week || 0;
}

// ============================================
// SCHEDULE DISPLAY FUNCTIONS
// ============================================

/**
 * Display today's schedule
 */
async function displayTodaysSchedule() {
    const schedule = await loadTodaysSchedule();
    const container = document.getElementById('schedule-container');
    
    if (!container) return;
    
    if (schedule.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📋</div>
                <p>No medications scheduled for today</p>
                <a href="/add-medication" class="btn btn-primary mt-20">Add Medication</a>
            </div>
        `;
        return;
    }
    
    container.innerHTML = '<div class="schedule-list"></div>';
    const listContainer = container.querySelector('.schedule-list');
    
    schedule.forEach(item => {
        const scheduleItem = document.createElement('div');
        scheduleItem.className = 'schedule-item';
        
        const time = item.scheduled_time.split(' ')[1];
        
        scheduleItem.innerHTML = `
            <div class="schedule-info">
                <h3>${item.name}</h3>
                <p>Dosage: ${item.dosage} | Time: ${formatTime(time)}</p>
            </div>
            <div class="schedule-actions">
                <button class="btn btn-success btn-small" onclick="markTaken(${item.medication_id}, '${item.scheduled_time}')">
                    ✓ Taken
                </button>
                <button class="btn btn-danger btn-small" onclick="markMissed(${item.medication_id}, '${item.scheduled_time}')">
                    ✗ Missed
                </button>
            </div>
        `;
        
        listContainer.appendChild(scheduleItem);
    });
}

/**
 * Mark dose as taken
 */
async function markTaken(medicationId, scheduledTime) {
    const success = await recordDose(medicationId, scheduledTime, 'taken');
    
    if (success) {
        displayTodaysSchedule();
    }
}

/**
 * Mark dose as missed
 */
async function markMissed(medicationId, scheduledTime) {
    const success = await recordDose(medicationId, scheduledTime, 'missed');
    
    if (success) {
        displayTodaysSchedule();
    }
}

// ============================================
// ACTIVE NAVIGATION
// ============================================

/**
 * Set active navigation item
 */
function setActiveNav() {
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav a');
    
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        } else {
            link.classList.remove('active');
        }
    });
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Set active navigation
    setActiveNav();
    
    // Load dashboard data if on index page
    if (window.location.pathname === '/') {
        displayStatistics();
        displayTodaysSchedule();
    }
});

// Make functions globally available
window.markTaken = markTaken;
window.markMissed = markMissed;