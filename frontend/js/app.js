/**
 * Fiscal Pilot - Main Application Logic
 */

// API Configuration
const API_BASE = '/api';
let authToken = localStorage.getItem('fiscal_pilot_token');
function isAuthenticated() {
    authToken = localStorage.getItem('fiscal_pilot_token');
    return !!authToken;
}

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
localStorage.removeItem('fiscal_pilot_token');
localStorage.removeItem('fiscal_pilot_user');
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

// Plaid Functions (Bank Account Integration)
// NOTE: This uses Plaid sandbox (demo only), not RBI Account Aggregator
async function createPlaidLinkToken() {
    return apiRequest('/plaid/create-link-token', {
        method: 'POST'
    });
}

async function exchangePlaidPublicToken(publicToken) {
    return apiRequest('/plaid/exchange-public-token', {
        method: 'POST',
        body: { public_token: publicToken }
    });
}

async function syncPlaidTransactions() {
    return apiRequest('/plaid/sync-transactions');
}

async function getPlaidStatus() {
    return apiRequest('/plaid/status');
}

// Autonomous Agent Functions
// NOTE: This is an autonomous agent, NOT a chatbot
async function getAgentStatus() {
    return apiRequest('/agent/status');
}

async function getAgentActions(unresolvedOnly = false) {
    return apiRequest(`/agent/actions?unresolved_only=${unresolvedOnly}`);
}

async function resolveAgentAction(actionId) {
    return apiRequest(`/agent/actions/${actionId}/resolve`, {
        method: 'POST'
    });
}

async function triggerAgent() {
    return apiRequest('/agent/trigger', {
        method: 'POST'
    });
}

function initializePlaidLink() {
    /**
     * Initialize Plaid Link for bank account connection
     * NOTE: This uses Plaid sandbox for demonstration purposes only
     */
    return new Promise(async (resolve, reject) => {
        try {
            // Check if Plaid is loaded
            if (typeof Plaid === 'undefined') {
                reject(new Error('Plaid Link library not loaded. Please include Plaid Link script.'));
                return;
            }

            // Get link token from backend
            const tokenResponse = await createPlaidLinkToken();
            const linkToken = tokenResponse.link_token;

            // Create Plaid Link handler
            const handler = Plaid.create({
                token: linkToken,
                onSuccess: async (publicToken, metadata) => {
                    try {
                        // Exchange public token for access token (server-side)
                        await exchangePlaidPublicToken(publicToken);
                        resolve({
                            success: true,
                            message: 'Bank Connected ✅',
                            metadata: metadata
                        });
                    } catch (error) {
                        reject(error);
                    }
                },
                onExit: (err, metadata) => {
                    if (err != null) {
                        reject(new Error(`Plaid Link error: ${err.display_message || err.error_message || 'Unknown error'}`));
                    } else {
                        // User closed without connecting
                        resolve({
                            success: false,
                            cancelled: true,
                            message: 'Bank connection cancelled'
                        });
                    }
                },
                onEvent: (eventName, metadata) => {
                    // Optional: Log Plaid Link events for debugging
                    console.log('Plaid Link event:', eventName, metadata);
                }
            });

            // Open Plaid Link
            handler.open();
        } catch (error) {
            reject(error);
        }
    });
}

// Utility Functions
function formatCurrency(amount) {
    return new Intl.NumberFormat('USD', {
        style: 'currency',
        currency: 'USD',
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
    createPlaidLinkToken,
    exchangePlaidPublicToken,
    syncPlaidTransactions,
    getPlaidStatus,
    initializePlaidLink,
    getAgentStatus,
    getAgentActions,
    resolveAgentAction,
    triggerAgent,
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
