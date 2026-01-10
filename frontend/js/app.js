/**
 * Fiscal Pilot - Main Application Logic
 */

// API Configuration
const API_BASE = '/api';
let authToken = localStorage.getItem('fiscal_pilot_token');

// API Helper Functions
async function apiRequest(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    const config = {
        headers: {
            'Content-Type': 'application/json',
            ...(authToken && { 'Authorization': `Bearer ${authToken}` })
        },
        ...options
    };
    
    if (config.body && typeof config.body === 'object') {
        config.body = JSON.stringify(config.body);
    }
    
    try {
        const response = await fetch(url, config);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }
        
        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Auth Functions
async function login(email, password) {
    const data = await apiRequest('/auth/login', {
        method: 'POST',
        body: { email, password }
    });
    
    if (data.token) {
        authToken = data.token;
        localStorage.setItem('fiscal_pilot_token', authToken);
        localStorage.setItem('fiscal_pilot_user', JSON.stringify(data.user));
    }
    
    return data;
}

async function register(email, password, fullName, consent) {
    const data = await apiRequest('/auth/register', {
        method: 'POST',
        body: { email, password, full_name: fullName, data_consent: consent }
    });
    
    if (data.token) {
        authToken = data.token;
        localStorage.setItem('fiscal_pilot_token', authToken);
        localStorage.setItem('fiscal_pilot_user', JSON.stringify(data.user));
    }
    
    return data;
}

function logout() {
    authToken = null;
    localStorage.removeItem('fiscal_pilot_token');
    localStorage.removeItem('fiscal_pilot_user');
    window.location.href = '/';
}

function isAuthenticated() {
    return !!authToken;
}

function getCurrentUser() {
    const userStr = localStorage.getItem('fiscal_pilot_user');
    return userStr ? JSON.parse(userStr) : null;
}

// Transaction Functions
async function getTransactions(days = 90) {
    return apiRequest(`/transactions?days=${days}`);
}

async function createTransaction(transaction) {
    return apiRequest('/transactions', {
        method: 'POST',
        body: transaction
    });
}

async function deleteTransaction(id) {
    return apiRequest(`/transactions/${id}`, {
        method: 'DELETE'
    });
}

async function uploadTransactionsCSV(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    const url = `${API_BASE}/transactions/upload-csv`;
    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${authToken}`
        },
        body: formData
    });
    
    const data = await response.json();
    
    if (!response.ok) {
        throw new Error(data.error || 'Upload failed');
    }
    
    return data;
}

// Analysis Functions
async function runFullAnalysis() {
    return apiRequest('/analysis/full-analysis', {
        method: 'POST'
    });
}

async function getRiskProfile() {
    return apiRequest('/analysis/risk-profile');
}

async function getInsights() {
    return apiRequest('/analysis/insights');
}

// Preferences Functions
async function getPreferences() {
    return apiRequest('/preferences');
}

async function updatePreferences(preferences) {
    return apiRequest('/preferences', {
        method: 'PUT',
        body: preferences
    });
}

// Utility Functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: 'INR',
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('en-IN', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    }).format(date);
}

function showAlert(message, type = 'info', container = document.body) {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    container.insertBefore(alert, container.firstChild);
    
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

function showLoading(element) {
    if (element) {
        element.innerHTML = '<div class="loading"></div>';
    }
}

// Export for global use
window.app = {
    apiRequest,
    login,
    register,
    logout,
    isAuthenticated,
    getCurrentUser,
    getTransactions,
    createTransaction,
    deleteTransaction,
    uploadTransactionsCSV,
    runFullAnalysis,
    getRiskProfile,
    getInsights,
    getPreferences,
    updatePreferences,
    formatCurrency,
    formatDate,
    showAlert,
    showLoading
};

// Initialize theme toggle button
document.addEventListener('DOMContentLoaded', function() {
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            window.themeManager?.toggleTheme();
        });
    }
});
