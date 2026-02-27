// AI Employee Vault Dashboard - Enhanced JavaScript

// Global state
let refreshInterval = null;
let activityInterval = null;
let systemMetricsInterval = null;
let currentTask = null;
let activityChart = null;
let distributionChart = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    console.log('🤖 AI Employee Vault Dashboard initialized');
    initializeDashboard();
    setupEventListeners();
    startAutoRefresh();
    startSystemTime();
    initializeCharts();
});

// Initialize dashboard
async function initializeDashboard() {
    await refreshDashboard();
    await loadSystemMetrics();
    await loadRecentActivity();
}

// Setup event listeners
function setupEventListeners() {
    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            switchTab(this.dataset.tab);
        });
    });

    // Chart period buttons
    document.querySelectorAll('.chart-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.chart-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            updateChartPeriod(this.dataset.period);
        });
    });
}

// Start auto-refresh
function startAutoRefresh() {
    refreshInterval = setInterval(refreshDashboard, 30000); // 30 seconds
    activityInterval = setInterval(loadRecentActivity, 10000); // 10 seconds
    systemMetricsInterval = setInterval(loadSystemMetrics, 5000); // 5 seconds
}

// Update system time
function startSystemTime() {
    updateSystemTime();
    setInterval(updateSystemTime, 1000);
}

function updateSystemTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', { hour12: false });
    document.getElementById('systemTime').textContent = timeString;
}

// Refresh entire dashboard
async function refreshDashboard() {
    try {
        await Promise.all([
            loadOverview(),
            loadTasks()
        ]);
        addActivityLog('SYSTEM', 'Dashboard refreshed');
    } catch (error) {
        console.error('Error refreshing dashboard:', error);
        addActivityLog('ERROR', 'Failed to refresh dashboard');
    }
}

// Load overview statistics
async function loadOverview() {
    try {
        const response = await fetch('/api/overview');
        const data = await response.json();

        // Update memory banks
        animateValue('memoryNeedsAction', data.needs_action.total);
        animateValue('memoryPending', data.pending_approval.total);
        animateValue('memoryApproved', data.approved.total);
        animateValue('memoryDone', data.done_total);

        // Update stats cards
        animateValue('statToday', data.done_today);
        animateValue('statWeek', data.done_this_week);
        animateValue('statTotal', data.done_total);
        document.getElementById('statSuccessRate').textContent = data.success_rate + '%';

        // Update skill usage bars
        const totalTasks = data.needs_action.total + data.pending_approval.total + data.approved.total;
        const maxTasks = Math.max(totalTasks, 10);

        const whatsappCount = data.needs_action.by_type.whatsapp + data.pending_approval.by_type.whatsapp + data.approved.by_type.whatsapp;
        const emailCount = data.needs_action.by_type.email + data.pending_approval.by_type.email + data.approved.by_type.email;
        const linkedinCount = data.needs_action.by_type.linkedin + data.pending_approval.by_type.linkedin + data.approved.by_type.linkedin;

        updateProgressBar('skillWhatsApp', whatsappCount, maxTasks);
        updateProgressBar('skillEmail', emailCount, maxTasks);
        updateProgressBar('skillLinkedIn', linkedinCount, maxTasks);

        document.getElementById('skillWhatsAppValue').textContent = whatsappCount;
        document.getElementById('skillEmailValue').textContent = emailCount;
        document.getElementById('skillLinkedInValue').textContent = linkedinCount;

        // Update pipeline stages
        updatePipelineStages(data);

        // Update watcher status
        updateWatcherStatus('WhatsApp', data.watchers.whatsapp);
        updateWatcherStatus('Gmail', data.watchers.gmail);
        updateWatcherStatus('LinkedIn', data.watchers.linkedin);

        // Update distribution chart
        updateDistributionChart(data);

    } catch (error) {
        console.error('Error loading overview:', error);
        addActivityLog('ERROR', 'Failed to load overview data');
    }
}

// Animate number value
function animateValue(elementId, targetValue) {
    const element = document.getElementById(elementId);
    const currentValue = parseInt(element.textContent) || 0;
    const duration = 500;
    const steps = 20;
    const increment = (targetValue - currentValue) / steps;
    let current = currentValue;
    let step = 0;

    const timer = setInterval(() => {
        step++;
        current += increment;
        element.textContent = Math.round(current);

        if (step >= steps) {
            element.textContent = targetValue;
            clearInterval(timer);
        }
    }, duration / steps);
}

// Update progress bar
function updateProgressBar(elementId, value, max) {
    const percent = max > 0 ? (value / max * 100) : 0;
    const element = document.getElementById(elementId);
    element.style.width = Math.min(percent, 100) + '%';
}

// Update pipeline stages
function updatePipelineStages(data) {
    const processing = document.getElementById('stageProcessing');
    const approval = document.getElementById('stageApproval');
    const execution = document.getElementById('stageExecution');

    // Processing stage active if tasks in needs action
    if (data.needs_action.total > 0) {
        processing.classList.add('active');
    } else {
        processing.classList.remove('active');
    }

    // Approval stage active if tasks in pending approval
    if (data.pending_approval.total > 0) {
        approval.classList.add('active');
    } else {
        approval.classList.remove('active');
    }

    // Execution stage active if tasks in approved
    if (data.approved.total > 0) {
        execution.classList.add('active');
    } else {
        execution.classList.remove('active');
    }
}

// Update watcher status
function updateWatcherStatus(name, isOnline) {
    const watcherId = 'watcher' + name.replace(/\s/g, '');
    const watcherElement = document.getElementById(watcherId);

    if (watcherElement) {
        const statusElement = watcherElement.querySelector('.watcher-status');

        if (isOnline) {
            watcherElement.classList.add('online');
            statusElement.textContent = 'Online';
            statusElement.classList.remove('offline');
            statusElement.classList.add('online');
        } else {
            watcherElement.classList.remove('online');
            statusElement.textContent = 'Offline';
            statusElement.classList.remove('online');
            statusElement.classList.add('offline');
        }
    }
}

// Load system metrics
async function loadSystemMetrics() {
    try {
        const response = await fetch('/api/system/metrics');
        const data = await response.json();

        // Update CPU
        document.getElementById('cpuPercent').textContent = data.cpu.percent + '%';
        document.getElementById('cpuBar').style.width = data.cpu.percent + '%';

        // Update Memory
        document.getElementById('memoryPercent').textContent = data.memory.percent + '%';
        document.getElementById('memoryBar').style.width = data.memory.percent + '%';

        // Update Disk
        document.getElementById('diskPercent').textContent = data.disk.percent + '%';
        document.getElementById('diskBar').style.width = data.disk.percent + '%';

        // Update Uptime
        document.getElementById('systemUptime').textContent = data.uptime;

    } catch (error) {
        console.error('Error loading system metrics:', error);
    }
}

// Load recent activity
async function loadRecentActivity() {
    try {
        const response = await fetch('/api/activity/recent');
        const data = await response.json();

        const activityFeed = document.getElementById('activityFeed');
        activityFeed.innerHTML = '';

        data.activities.slice(0, 10).forEach(activity => {
            const time = new Date(activity.timestamp).toLocaleTimeString('en-US', { hour12: false });
            const item = document.createElement('div');
            item.className = 'activity-item';
            item.innerHTML = `
                <div class="activity-time">${time}</div>
                <div class="activity-text">${activity.action}: ${activity.filename}</div>
            `;
            activityFeed.appendChild(item);
        });

    } catch (error) {
        console.error('Error loading activity:', error);
    }
}

// Add activity log
function addActivityLog(type, message) {
    const activityFeed = document.getElementById('activityFeed');
    const time = new Date().toLocaleTimeString('en-US', { hour12: false });

    const item = document.createElement('div');
    item.className = 'activity-item';
    item.innerHTML = `
        <div class="activity-time">${time}</div>
        <div class="activity-text">[${type}] ${message}</div>
    `;

    activityFeed.insertBefore(item, activityFeed.firstChild);

    // Keep only last 10 items
    while (activityFeed.children.length > 10) {
        activityFeed.removeChild(activityFeed.lastChild);
    }
}

// Initialize charts
function initializeCharts() {
    initializeActivityChart();
    initializeDistributionChart();
}

// Initialize activity chart
async function initializeActivityChart() {
    try {
        const response = await fetch('/api/analytics/hourly');
        const data = await response.json();

        const ctx = document.getElementById('activityChart').getContext('2d');
        activityChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels.reverse(),
                datasets: [{
                    label: 'Tasks Completed',
                    data: data.data.reverse(),
                    borderColor: '#00D4FF',
                    backgroundColor: 'rgba(0, 212, 255, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            color: '#8FA3BF',
                            stepSize: 1
                        },
                        grid: {
                            color: 'rgba(0, 212, 255, 0.1)'
                        }
                    },
                    x: {
                        ticks: {
                            color: '#8FA3BF'
                        },
                        grid: {
                            color: 'rgba(0, 212, 255, 0.1)'
                        }
                    }
                }
            }
        });
    } catch (error) {
        console.error('Error initializing activity chart:', error);
    }
}

// Initialize distribution chart
function initializeDistributionChart() {
    const ctx = document.getElementById('distributionChart').getContext('2d');
    distributionChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Email', 'WhatsApp', 'LinkedIn', 'Other'],
            datasets: [{
                data: [0, 0, 0, 0],
                backgroundColor: [
                    '#EA4335',
                    '#25D366',
                    '#0077B5',
                    '#8FA3BF'
                ],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#8FA3BF',
                        padding: 15,
                        font: {
                            size: 11
                        }
                    }
                }
            }
        }
    });
}

// Update distribution chart
function updateDistributionChart(data) {
    if (distributionChart) {
        const total = data.needs_action.total + data.pending_approval.total + data.approved.total;

        if (total > 0) {
            const emailCount = data.needs_action.by_type.email + data.pending_approval.by_type.email + data.approved.by_type.email;
            const whatsappCount = data.needs_action.by_type.whatsapp + data.pending_approval.by_type.whatsapp + data.approved.by_type.whatsapp;
            const linkedinCount = data.needs_action.by_type.linkedin + data.pending_approval.by_type.linkedin + data.approved.by_type.linkedin;
            const otherCount = data.needs_action.by_type.other + data.pending_approval.by_type.other + data.approved.by_type.other;

            distributionChart.data.datasets[0].data = [emailCount, whatsappCount, linkedinCount, otherCount];
            distributionChart.update();
        }
    }
}

// Update chart period
async function updateChartPeriod(period) {
    // TODO: Implement different time periods
    console.log('Switching to period:', period);
}

// Load tasks
async function loadTasks() {
    await loadTasksForFolder('pending-approval', 'tasksPending');
    await loadTasksForFolder('needs-action', 'tasksNeedsAction');
    await loadTasksForFolder('approved', 'tasksApproved');
    await loadTasksForFolder('done', 'tasksDone');
}

// Load tasks for specific folder
async function loadTasksForFolder(folder, containerId) {
    try {
        const response = await fetch(`/api/tasks/${folder}`);
        const data = await response.json();

        const container = document.getElementById(containerId);
        container.innerHTML = '';

        if (data.tasks.length === 0) {
            container.innerHTML = '<div class="loading-spinner">No tasks found</div>';
            return;
        }

        data.tasks.forEach(task => {
            const taskElement = createTaskElement(task, folder);
            container.appendChild(taskElement);
        });

    } catch (error) {
        console.error(`Error loading tasks for ${folder}:`, error);
        const container = document.getElementById(containerId);
        container.innerHTML = '<div class="loading-spinner">Error loading tasks</div>';
    }
}

// Create task element
function createTaskElement(task, folder) {
    const div = document.createElement('div');
    div.className = 'task-item';
    div.onclick = () => openTaskModal(task, folder);

    const taskType = task.type.includes('whatsapp') ? 'whatsapp' :
                     task.type.includes('email') ? 'email' :
                     task.type.includes('linkedin') ? 'linkedin' : 'other';

    const time = new Date(task.modified).toLocaleString();

    div.innerHTML = `
        <div class="task-header">
            <div class="task-title">${task.title}</div>
            <div class="task-badge ${taskType}">${taskType}</div>
        </div>
        <div class="task-meta">
            ${task.metadata.from ? `From: ${task.metadata.from} | ` : ''}
            ${time}
        </div>
    `;

    return div;
}

// Switch tab
function switchTab(tabName) {
    // Update tab buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Update tab content
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    document.getElementById(`tab-${tabName}`).classList.add('active');
}

// Open task modal
function openTaskModal(task, folder) {
    currentTask = { ...task, folder };

    const modal = document.getElementById('taskModal');
    const modalTitle = document.getElementById('modalTitle');
    const modalBody = document.getElementById('modalBody');

    modalTitle.textContent = task.title;
    modalBody.innerHTML = `
        <div style="white-space: pre-wrap; font-family: 'JetBrains Mono', monospace; font-size: 12px; line-height: 1.6;">
${task.body}
        </div>
    `;

    // Show/hide approve/reject buttons based on folder
    const btnApprove = document.getElementById('btnApprove');
    const btnReject = document.getElementById('btnReject');

    if (folder === 'pending-approval') {
        btnApprove.style.display = 'inline-block';
        btnReject.style.display = 'inline-block';
    } else {
        btnApprove.style.display = 'none';
        btnReject.style.display = 'none';
    }

    modal.classList.add('active');
}

// Close modal
function closeModal() {
    const modal = document.getElementById('taskModal');
    modal.classList.remove('active');
    currentTask = null;
}

// Approve task
async function approveTask() {
    if (!currentTask) return;

    try {
        const response = await fetch('/api/task/approve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: currentTask.filename })
        });

        const data = await response.json();

        if (data.success) {
            addActivityLog('APPROVAL', `Approved: ${currentTask.filename}`);
            closeModal();
            await refreshDashboard();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error approving task:', error);
        alert('Failed to approve task');
    }
}

// Reject task
async function rejectTask() {
    if (!currentTask) return;

    if (!confirm('Are you sure you want to reject this task?')) {
        return;
    }

    try {
        const response = await fetch('/api/task/reject', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename: currentTask.filename })
        });

        const data = await response.json();

        if (data.success) {
            addActivityLog('REJECTION', `Rejected: ${currentTask.filename}`);
            closeModal();
            await refreshDashboard();
        } else {
            alert('Error: ' + data.error);
        }
    } catch (error) {
        console.error('Error rejecting task:', error);
        alert('Failed to reject task');
    }
}

// Download logs
async function downloadLogs() {
    try {
        window.location.href = '/api/logs/download';
        addActivityLog('SYSTEM', 'Logs downloaded');
    } catch (error) {
        console.error('Error downloading logs:', error);
        alert('Failed to download logs');
    }
}

// Open settings
function openSettings() {
    alert('Settings panel coming soon!');
}

// Close modal on escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeModal();
    }
});

// Close modal on background click
document.getElementById('taskModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeModal();
    }
});
