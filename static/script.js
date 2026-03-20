const btnEvaluation = document.getElementById('btn-evaluation');
const btnCheckin = document.getElementById('btn-checkin');
const btnClearLogs = document.getElementById('btn-clear-logs');
const logContainer = document.getElementById('log-container');
const statusBadge = document.getElementById('bot-status-badge');

let lastLogCount = 0;
let pollInterval = null;

async function fetchStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.is_running) {
            statusBadge.textContent = `Running: ${data.current_task}`;
            statusBadge.className = 'status-badge running';
            btnEvaluation.disabled = true;
            btnCheckin.disabled = true;
            if (!pollInterval) startPolling();
        } else {
            statusBadge.textContent = 'Idle';
            statusBadge.className = 'status-badge idle';
            btnEvaluation.disabled = false;
            btnCheckin.disabled = false;
            if (pollInterval && !data.is_running) stopPolling();
        }
    } catch (error) {
        console.error('Error fetching status:', error);
    }
}

async function fetchLogs() {
    try {
        const response = await fetch('/api/logs');
        const data = await response.json();
        
        if (data.logs.length > lastLogCount) {
            const newLogs = data.logs.slice(lastLogCount);
            newLogs.forEach(log => {
                const entry = document.createElement('div');
                entry.className = 'log-entry info';
                if (log.toLowerCase().includes('error')) entry.classList.add('error');
                if (log.toLowerCase().includes('starting') || log.toLowerCase().includes('completed')) entry.classList.add('system');
                entry.textContent = `[${new Date().toLocaleTimeString()}] ${log}`;
                logContainer.appendChild(entry);
            });
            logContainer.scrollTop = logContainer.scrollHeight;
            lastLogCount = data.logs.length;
        }
    } catch (error) {
        console.error('Error fetching logs:', error);
    }
}

function startPolling() {
    pollInterval = setInterval(() => {
        fetchStatus();
        fetchLogs();
    }, 1000);
}

function stopPolling() {
    // Keep polling for a few seconds to catch final logs
    setTimeout(() => {
        clearInterval(pollInterval);
        pollInterval = null;
    }, 5000);
}

const usernameInput = document.getElementById('sts-username');
const passwordInput = document.getElementById('sts-password');

async function startTask(taskType) {
    const username = usernameInput.value.strip ? usernameInput.value.trim() : usernameInput.value;
    const password = passwordInput.value;

    if (!username || !password) {
        alert('Please enter your Student ID and PIN first.');
        return;
    }

    try {
        const response = await fetch(`/api/start/${taskType}`, { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await response.json();
        
        if (response.ok) {
            lastLogCount = 0;
            logContainer.innerHTML = '';
            const entry = document.createElement('div');
            entry.className = 'log-entry system';
            entry.textContent = `[${new Date().toLocaleTimeString()}] Initiative started: ${taskType}`;
            logContainer.appendChild(entry);
            fetchStatus();
        } else {
            alert(data.error || 'Failed to start task');
        }
    } catch (error) {
        console.error('Error starting task:', error);
    }
}

btnEvaluation.addEventListener('click', () => startTask('evaluation'));
btnCheckin.addEventListener('click', () => startTask('checkin'));
btnClearLogs.addEventListener('click', () => {
    logContainer.innerHTML = '';
    lastLogCount = 0;
});

// Initial load
fetchStatus();
setInterval(fetchStatus, 5000); // Regular status check if idle
