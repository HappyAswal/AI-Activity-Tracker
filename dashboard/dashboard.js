// Helper to get selected date or default to today
function getDateParam() {
    const datePicker = document.getElementById('datePicker');
    if (!datePicker.value) {
        const local = new Date();
        local.setMinutes(local.getMinutes() - local.getTimezoneOffset());
        datePicker.value = local.toJSON().slice(0, 10);
    }
    return datePicker.value;
}

// Chart instances
let pieChart = null;
let timelineChart = null;

// Load dashboard data
async function loadDashboard() {
    try {
        await Promise.all([
            loadSummary(),
            loadTimeline(),
            loadRecentActivity()
        ]);
    } catch (error) {
        console.error('Error loading dashboard:', error);
    }
}

// Load summary statistics
async function loadSummary() {
    const date = getDateParam();
    const response = await fetch(`/api/summary?date=${date}`);
    const data = await response.json();

    document.getElementById('focused-hours').textContent = `${data.focused_hours}h`;
    document.getElementById('distracted-hours').textContent = `${data.distracted_hours}h`;
    document.getElementById('idle-hours').textContent = `${data.idle_hours}h`;
    document.getElementById('total-hours').textContent = `${data.total_tracked_hours}h`;

    // Update pie chart
    updatePieChart(data);
}

// Load timeline data
async function loadTimeline() {
    const date = getDateParam();
    const response = await fetch(`/api/timeline?date=${date}`);
    const data = await response.json();

    updateTimelineChart(data);
}

// Load recent activity
async function loadRecentActivity() {
    const date = getDateParam();
    const response = await fetch(`/api/recent?limit=15&date=${date}`);
    const data = await response.json();

    const activityList = document.getElementById('activity-list');

    if (data.length === 0) {
        activityList.innerHTML = '<div class="loading">No activity recorded yet</div>';
        return;
    }

    activityList.innerHTML = data.map(activity => {
        const time = new Date(activity.timestamp).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });

        const categoryClass = activity.category.toLowerCase().replace(' ', '-');

        return `
            <div class="activity-item">
                <div class="activity-time">${time}</div>
                <div class="activity-category category-${categoryClass}">
                    ${activity.category}
                </div>
                <div class="activity-details">
                    <div class="activity-app">${activity.app_name}</div>
                    <div class="activity-title">${activity.window_title}</div>
                </div>
            </div>
        `;
    }).join('');
}

// Update pie chart
function updatePieChart(data) {
    const ctx = document.getElementById('pieChart').getContext('2d');

    if (pieChart) {
        pieChart.destroy();
    }

    pieChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Focused', 'Distracted', 'Communication', 'Other', 'Idle'],
            datasets: [{
                data: [
                    data.focused_hours,
                    data.distracted_hours,
                    data.communication_hours,
                    data.other_hours,
                    data.idle_hours
                ],
                backgroundColor: [
                    'rgba(16, 185, 129, 0.8)',
                    'rgba(239, 68, 68, 0.8)',
                    'rgba(59, 130, 246, 0.8)',
                    'rgba(139, 92, 246, 0.8)',
                    'rgba(245, 158, 11, 0.8)'
                ],
                borderColor: [
                    'rgba(16, 185, 129, 1)',
                    'rgba(239, 68, 68, 1)',
                    'rgba(59, 130, 246, 1)',
                    'rgba(139, 92, 246, 1)',
                    'rgba(245, 158, 11, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#e4e7f1',
                        padding: 15,
                        font: {
                            size: 12,
                            family: 'Inter'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    titleColor: '#e4e7f1',
                    bodyColor: '#e4e7f1',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: true,
                    callbacks: {
                        label: function (context) {
                            return `${context.label}: ${context.parsed.toFixed(2)}h`;
                        }
                    }
                }
            }
        }
    });
}

// Update timeline chart
function updateTimelineChart(data) {
    const ctx = document.getElementById('timelineChart').getContext('2d');

    if (timelineChart) {
        timelineChart.destroy();
    }

    const hours = data.map(d => `${d.hour}:00`);

    timelineChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: hours,
            datasets: [
                {
                    label: 'Productivity',
                    data: data.map(d => d.Productivity),
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Entertainment',
                    data: data.map(d => d.Entertainment),
                    backgroundColor: 'rgba(239, 68, 68, 0.8)',
                    borderColor: 'rgba(239, 68, 68, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Social Media',
                    data: data.map(d => d['Social Media']),
                    backgroundColor: 'rgba(245, 158, 11, 0.8)',
                    borderColor: 'rgba(245, 158, 11, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Communication',
                    data: data.map(d => d.Communication),
                    backgroundColor: 'rgba(59, 130, 246, 0.8)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                x: {
                    stacked: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: '#9ca3af',
                        font: {
                            size: 11,
                            family: 'Inter'
                        }
                    }
                },
                y: {
                    stacked: true,
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    },
                    ticks: {
                        color: '#9ca3af',
                        font: {
                            size: 11,
                            family: 'Inter'
                        },
                        callback: function (value) {
                            return value + 'm';
                        }
                    },
                    title: {
                        display: true,
                        text: 'Minutes',
                        color: '#9ca3af',
                        font: {
                            size: 12,
                            family: 'Inter'
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#e4e7f1',
                        padding: 15,
                        font: {
                            size: 12,
                            family: 'Inter'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(15, 23, 42, 0.9)',
                    titleColor: '#e4e7f1',
                    bodyColor: '#e4e7f1',
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    borderWidth: 1,
                    padding: 12,
                    callbacks: {
                        label: function (context) {
                            return `${context.dataset.label}: ${context.parsed.y.toFixed(1)}m`;
                        }
                    }
                }
            }
        }
    });
}

// Auto-refresh every 60 seconds
setInterval(loadDashboard, 60000);

// Initial load
loadDashboard();
