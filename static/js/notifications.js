// static/js/notifications.js
// Notification and reminder system

// ============================================
// NOTIFICATION SETUP
// ============================================

/**
 * Request notification permission
 */
function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                console.log('Notification permission granted');
            }
        });
    }
}

/**
 * Show browser notification
 */
function showNotification(title, body, icon = '💊') {
    if ('Notification' in window && Notification.permission === 'granted') {
        const notification = new Notification(title, {
            body: body,
            icon: icon,
            badge: icon,
            requireInteraction: true
        });
        
        // Play alarm sound
        playAlarmSound();
        
        notification.onclick = function() {
            window.focus();
            notification.close();
        };
    }
}

/**
 * Play alarm sound
 */
function playAlarmSound() {
    const audio = new Audio('/static/sounds/alarm.mp3');
    audio.play().catch(err => {
        console.log('Could not play alarm sound:', err);
    });
}

// ============================================
// REMINDER CHECKING
// ============================================

/**
 * Check for upcoming medications
 */
async function checkUpcomingReminders() {
    const result = await fetch('/api/todays-schedule');
    const data = await result.json();
    
    if (!data.success) return;
    
    const now = new Date();
    const schedule = data.data;
    
    schedule.forEach(item => {
        const scheduledTime = new Date(item.scheduled_time);
        const timeDiff = (scheduledTime - now) / 1000 / 60; // Minutes
        
        // Remind 15 minutes before
        if (timeDiff > 0 && timeDiff <= 15) {
            showNotification(
                'Medication Reminder',
                `Time to take ${item.name} (${item.dosage}) in ${Math.round(timeDiff)} minutes`,
                '⏰'
            );
        }
        
        // Remind at exact time
        if (timeDiff > -1 && timeDiff <= 0) {
            showNotification(
                'Take Your Medication Now!',
                `${item.name} (${item.dosage})`,
                '💊'
            );
        }
    });
}

/**
 * Start reminder checking loop
 */
function startReminderSystem() {
    // Request permission on page load
    requestNotificationPermission();
    
    // Check every 60 seconds
    setInterval(checkUpcomingReminders, 60000);
    
    // Check immediately
    checkUpcomingReminders();
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    startReminderSystem();
});