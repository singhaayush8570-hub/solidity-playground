const API_BASE = window.location.origin;
let currentResult = null;
let inputHistory = [];
let historyIndex = -1;

function appendDisplay(value) {
    const display = document.getElementById('display');
    if (value === '!' || value === 'exp(') {
        // These need special handling
        display.value += value;
    } else {
        display.value += value;
    }
}

function deleteDisplay() {
    const display = document.getElementById('display');
    display.value = display.value.slice(0, -1);
}

function clearDisplay() {
    document.getElementById('display').value = '';
}

async function calculate() {
    const display = document.getElementById('display');
    const expression = display.value.trim();
    
    if (!expression) {
        showNotification('Please enter an expression', 'warning');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/calculate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ expression })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            display.value = data.result;
            currentResult = data.result;
            showNotification('✓ Calculated successfully!', 'success');
            loadStatistics();
        } else {
            display.value = data.error || 'Error';
            showNotification(data.error, 'error');
        }
    } catch (error) {
        display.value = 'Error';
        showNotification('Network error: ' + error.message, 'error');
    }
}

function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active from nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName).classList.add('active');
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    
    if (tabName === 'history') loadHistory();
    if (tabName === 'stats') loadStatistics();
}

async function loadHistory() {
    try {
        const response = await fetch(`${API_BASE}/api/history?limit=100`);
        const history = await response.json();
        
        const list = document.getElementById('history-list');
        
        if (history.length === 0) {
            list.innerHTML = '<div style="text-align: center; color: #9ca3af; padding: 40px;"><i class="fas fa-inbox"></i> No calculations yet</div>';
            return;
        }
        
        list.innerHTML = history.map(item => `
            <div class="history-item">
                <div class="history-content">
                    <div class="history-expr">${escapeHtml(item.expression)}</div>
                    <div class="history-result">= ${escapeHtml(item.result)}</div>
                    <div class="history-time">${new Date(item.timestamp).toLocaleString()}</div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

async function searchHistory() {
    const query = document.getElementById('search-input').value;
    
    if (!query) {
        loadHistory();
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/history/search?q=${encodeURIComponent(query)}`);
        const results = await response.json();
        
        const list = document.getElementById('history-list');
        
        if (results.length === 0) {
            list.innerHTML = '<div style="text-align: center; color: #9ca3af; padding: 40px;">No results found</div>';
            return;
        }
        
        list.innerHTML = results.map(item => `
            <div class="history-item">
                <div class="history-content">
                    <div class="history-expr">${escapeHtml(item.expression)}</div>
                    <div class="history-result">= ${escapeHtml(item.result)}</div>
                    <div class="history-time">${new Date(item.timestamp).toLocaleString()}</div>
                </div>
            </div>
        `).join('');
    } catch (error) {
        showNotification('Search error: ' + error.message, 'error');
    }
}

async function clearAllHistory() {
    if (!confirm('Are you sure you want to clear all history?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/api/history/clear`, { method: 'DELETE' });
        if (response.ok) {
            loadHistory();
            showNotification('✓ History cleared', 'success');
        }
    } catch (error) {
        showNotification('Error clearing history', 'error');
    }
}

async function solveQuadratic() {
    const a = parseFloat(document.getElementById('quad-a').value);
    const b = parseFloat(document.getElementById('quad-b').value);
    const c = parseFloat(document.getElementById('quad-c').value);
    const resultDiv = document.getElementById('quad-result');
    
    if (isNaN(a) || isNaN(b) || isNaN(c)) {
        resultDiv.innerHTML = '<span style="color: var(--danger);">Please enter valid numbers</span>';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/advanced/quadratic`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ a, b, c })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            resultDiv.innerHTML = `
                <div style="color: var(--primary); text-align: left;">
                    <strong>Type:</strong> ${data.type}<br>
                    <strong>x₁ =</strong> ${data.x1}<br>
                    <strong>x₂ =</strong> ${data.x2}<br>
                    <strong>Δ =</strong> ${data.discriminant.toFixed(2)}
                </div>
            `;
            showNotification('✓ Solved!', 'success');
        } else {
            resultDiv.innerHTML = `<span style="color: var(--danger);">${data.error}</span>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `<span style="color: var(--danger);">Error: ${error.message}</span>`;
    }
}

async function calculateFactorial() {
    const n = parseInt(document.getElementById('fact-n').value);
    const resultDiv = document.getElementById('fact-result');
    
    if (isNaN(n) || n < 0 || n > 170) {
        resultDiv.innerHTML = '<span style="color: var(--danger);">Enter integer between 0-170</span>';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/advanced/factorial`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ n })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            resultDiv.innerHTML = `<span style="color: var(--primary);"><strong>${n}! =</strong> ${data.result}</span>`;
            showNotification('✓ Calculated!', 'success');
        } else {
            resultDiv.innerHTML = `<span style="color: var(--danger);">${data.error}</span>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `<span style="color: var(--danger);">Error: ${error.message}</span>`;
    }
}

async function generateFibonacci() {
    const n = parseInt(document.getElementById('fib-n').value);
    const resultDiv = document.getElementById('fib-result');
    
    if (isNaN(n) || n < 1) {
        resultDiv.innerHTML = '<span style="color: var(--danger);">Enter positive number</span>';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/advanced/fibonacci`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ n })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            resultDiv.innerHTML = `<span style="color: var(--primary);"><strong>Sequence:</strong> ${data.result.join(', ')}</span>`;
            showNotification('✓ Generated!', 'success');
        } else {
            resultDiv.innerHTML = `<span style="color: var(--danger);">${data.error}</span>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `<span style="color: var(--danger);">Error: ${error.message}</span>`;
    }
}

async function getPrimeFactors() {
    const n = parseInt(document.getElementById('prime-n').value);
    const resultDiv = document.getElementById('prime-result');
    
    if (isNaN(n) || n < 2) {
        resultDiv.innerHTML = '<span style="color: var(--danger);">Enter number ≥ 2</span>';
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/api/advanced/prime-factors`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ n })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            resultDiv.innerHTML = `<span style="color: var(--primary);"><strong>Factors:</strong> ${data.result.join(' × ')}</span>`;
            showNotification('✓ Factorized!', 'success');
        } else {
            resultDiv.innerHTML = `<span style="color: var(--danger);">${data.error}</span>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `<span style="color: var(--danger);">Error: ${error.message}</span>`;
    }
}

async function loadStatistics() {
    try {
        const response = await fetch(`${API_BASE}/api/statistics`);
        const stats = await response.json();
        
        document.getElementById('stat-total').textContent = stats.total_calculations;
        document.getElementById('stat-op').textContent = stats.most_used_operation || '-';
    } catch (error) {
        console.error('Error loading statistics:', error);
    }
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Keyboard support
document.addEventListener('keydown', (e) => {
    if (e.key >= '0' && e.key <= '9') appendDisplay(e.key);
    else if (e.key === '+' || e.key === '-' || e.key === '*' || e.key === '/') appendDisplay(e.key);
    else if (e.key === 'Enter') calculate();
    else if (e.key === 'Backspace') deleteDisplay();
    else if (e.key === 'Escape') clearDisplay();
    else if (e.key === '.') appendDisplay('.');
});

const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);

document.addEventListener('DOMContentLoaded', () => {
    loadStatistics();
    document.getElementById('calculator').classList.add('active');
});
