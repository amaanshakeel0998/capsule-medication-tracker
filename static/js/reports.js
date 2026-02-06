// static/js/reports.js
// Report generation and visualization

// ============================================
// ADHERENCE REPORT
// ============================================

/**
 * Load and display adherence report
 */
async function loadAdherenceReport() {
    const result = await fetch('/api/ai/analyze-adherence?days=30');
    const data = await result.json();
    
    if (!data.success) return;
    
    const adherence = data.data;
    
    // Display adherence rate
    document.getElementById('adherence-rate').textContent = adherence.adherence_rate + '%';
    document.getElementById('total-doses').textContent = adherence.total_doses;
    document.getElementById('doses-taken').textContent = adherence.taken;
    document.getElementById('doses-missed').textContent = adherence.missed;
    document.getElementById('doses-delayed').textContent = adherence.delayed;
    
    // Create adherence pie chart
    createAdherencePieChart(adherence);
}

/**
 * Create adherence pie chart
 */
function createAdherencePieChart(adherence) {
    const canvas = document.getElementById('adherence-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const total = adherence.total_doses;
    
    if (total === 0) {
        ctx.fillStyle = '#a0aec0';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('No data available', canvas.width / 2, canvas.height / 2);
        return;
    }
    
    // Calculate percentages
    const takenPercent = (adherence.taken / total) * 100;
    const missedPercent = (adherence.missed / total) * 100;
    const delayedPercent = (adherence.delayed / total) * 100;
    
    // Draw pie chart
    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;
    const radius = Math.min(centerX, centerY) - 20;
    
    let currentAngle = -Math.PI / 2; // Start from top
    
    // Taken (green)
    ctx.fillStyle = '#48bb78';
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + (takenPercent / 100) * 2 * Math.PI);
    ctx.closePath();
    ctx.fill();
    currentAngle += (takenPercent / 100) * 2 * Math.PI;
    
    // Delayed (orange)
    ctx.fillStyle = '#ed8936';
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + (delayedPercent / 100) * 2 * Math.PI);
    ctx.closePath();
    ctx.fill();
    currentAngle += (delayedPercent / 100) * 2 * Math.PI;
    
    // Missed (red)
    ctx.fillStyle = '#f56565';
    ctx.beginPath();
    ctx.moveTo(centerX, centerY);
    ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + (missedPercent / 100) * 2 * Math.PI);
    ctx.closePath();
    ctx.fill();
    
    // Add legend
    drawLegend(ctx, canvas.width, canvas.height, adherence);
}

/**
 * Draw chart legend
 */
function drawLegend(ctx, width, height, adherence) {
    const legendX = 10;
    const legendY = height - 80;
    const boxSize = 15;
    const spacing = 25;
    
    // Taken
    ctx.fillStyle = '#48bb78';
    ctx.fillRect(legendX, legendY, boxSize, boxSize);
    ctx.fillStyle = '#2d3748';
    ctx.font = '12px Arial';
    ctx.textAlign = 'left';
    ctx.fillText(`Taken: ${adherence.taken}`, legendX + boxSize + 5, legendY + 12);
    
    // Delayed
    ctx.fillStyle = '#ed8936';
    ctx.fillRect(legendX, legendY + spacing, boxSize, boxSize);
    ctx.fillStyle = '#2d3748';
    ctx.fillText(`Delayed: ${adherence.delayed}`, legendX + boxSize + 5, legendY + spacing + 12);
    
    // Missed
    ctx.fillStyle = '#f56565';
    ctx.fillRect(legendX, legendY + spacing * 2, boxSize, boxSize);
    ctx.fillStyle = '#2d3748';
    ctx.fillText(`Missed: ${adherence.missed}`, legendX + boxSize + 5, legendY + spacing * 2 + 12);
}

// ============================================
// DOSE HISTORY
// ============================================

/**
 * Load and display dose history
 */
async function loadDoseHistory() {
    const result = await fetch('/api/dose-history?days=30');
    const data = await result.json();
    
    if (!data.success) return;
    
    const history = data.data;
    const container = document.getElementById('history-table-body');
    
    if (!container) return;
    
    if (history.length === 0) {
        container.innerHTML = `
            <tr>
                <td colspan="5" class="text-center">No history available</td>
            </tr>
        `;
        return;
    }
    
    container.innerHTML = '';
    
    history.forEach(record => {
        const row = document.createElement('tr');
        
        const scheduledTime = new Date(record.scheduled_time);
        const actualTime = record.actual_time ? new Date(record.actual_time) : null;
        
        let statusBadge = '';
        if (record.status === 'taken') {
            statusBadge = '<span class="badge badge-taken">Taken</span>';
        } else if (record.status === 'missed') {
            statusBadge = '<span class="badge badge-missed">Missed</span>';
        } else if (record.status === 'delayed') {
            statusBadge = '<span class="badge badge-delayed">Delayed</span>';
        }
        
        row.innerHTML = `
            <td>${record.name}</td>
            <td>${record.dosage}</td>
            <td>${scheduledTime.toLocaleString()}</td>
            <td>${actualTime ? actualTime.toLocaleString() : '-'}</td>
            <td>${statusBadge}</td>
        `;
        
        container.appendChild(row);
    });
}

// ============================================
// WEEKLY TREND
// ============================================

/**
 * Load weekly trend
 */
async function loadWeeklyTrend() {
    const result = await fetch('/api/dose-history?days=7');
    const data = await result.json();
    
    if (!data.success) return;
    
    const history = data.data;
    
    // Group by date
    const dailyStats = {};
    
    history.forEach(record => {
        const date = record.scheduled_time.split(' ')[0];
        
        if (!dailyStats[date]) {
            dailyStats[date] = { taken: 0, missed: 0, delayed: 0 };
        }
        
        if (record.status === 'taken') {
            dailyStats[date].taken++;
        } else if (record.status === 'missed') {
            dailyStats[date].missed++;
        } else if (record.status === 'delayed') {
            dailyStats[date].delayed++;
        }
    });
    
    // Draw bar chart
    drawWeeklyChart(dailyStats);
}

/**
 * Draw weekly trend chart
 */
function drawWeeklyChart(dailyStats) {
    const canvas = document.getElementById('weekly-chart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const dates = Object.keys(dailyStats).sort();
    
    if (dates.length === 0) {
        ctx.fillStyle = '#a0aec0';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('No data available', canvas.width / 2, canvas.height / 2);
        return;
    }
    
    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    
    const barWidth = canvas.width / dates.length - 20;
    const maxValue = Math.max(...dates.map(date => 
        dailyStats[date].taken + dailyStats[date].missed + dailyStats[date].delayed
    ));
    
    const scale = (canvas.height - 50) / maxValue;
    
    dates.forEach((date, index) => {
        const x = index * (barWidth + 20) + 10;
        const stats = dailyStats[date];
        
        let y = canvas.height - 30;
        
        // Draw taken (green)
        if (stats.taken > 0) {
            const height = stats.taken * scale;
            ctx.fillStyle = '#48bb78';
            ctx.fillRect(x, y - height, barWidth, height);
            y -= height;
        }
        
        // Draw delayed (orange)
        if (stats.delayed > 0) {
            const height = stats.delayed * scale;
            ctx.fillStyle = '#ed8936';
            ctx.fillRect(x, y - height, barWidth, height);
            y -= height;
        }
        
        // Draw missed (red)
        if (stats.missed > 0) {
            const height = stats.missed * scale;
            ctx.fillStyle = '#f56565';
            ctx.fillRect(x, y - height, barWidth, height);
        }
        
        // Draw date label
        ctx.fillStyle = '#4a5568';
        ctx.font = '10px Arial';
        ctx.textAlign = 'center';
        const shortDate = new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        ctx.fillText(shortDate, x + barWidth / 2, canvas.height - 10);
    });
}

// ============================================
// INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    if (window.location.pathname === '/reports') {
        loadAdherenceReport();
        loadDoseHistory();
        loadWeeklyTrend();
    }
});