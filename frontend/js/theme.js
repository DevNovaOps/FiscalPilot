/**
 * Theme Management
 * Handles dark/light theme switching
 */

(function() {
    'use strict';
    
    const THEME_KEY = 'fiscal_pilot_theme';
    const DEFAULT_THEME = 'dark';
    
    // Initialize theme
    function initTheme() {
        const savedTheme = localStorage.getItem(THEME_KEY) || DEFAULT_THEME;
        setTheme(savedTheme);
    }
    
    // Set theme
    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem(THEME_KEY, theme);
        
        // Update toggle button icon
        const toggleBtn = document.getElementById('theme-toggle');
        if (toggleBtn) {
            toggleBtn.textContent = theme === 'dark' ? '☀️' : '🌙';
            toggleBtn.setAttribute('aria-label', `Switch to ${theme === 'dark' ? 'light' : 'dark'} theme`);
        }
    }
    
    // Toggle theme
    function toggleTheme() {
        const currentTheme = document.documentElement.getAttribute('data-theme') || DEFAULT_THEME;
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
    }
    
    // Initialize on load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTheme);
    } else {
        initTheme();
    }
    
    // Export for global use
    window.themeManager = {
        setTheme: setTheme,
        toggleTheme: toggleTheme,
        getTheme: () => document.documentElement.getAttribute('data-theme') || DEFAULT_THEME
    };
})();
