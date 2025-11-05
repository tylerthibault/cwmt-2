/**
 * Theme Management System
 * Handles dark/light mode switching with localStorage persistence
 */

(function() {
    'use strict';

    const ThemeManager = {
        STORAGE_KEY: 'cwmt-theme',
        THEMES: {
            LIGHT: 'light',
            DARK: 'dark'
        },

        /**
         * Initialize theme system
         */
        init: function() {
            // Apply saved theme immediately
            const savedTheme = this.getSavedTheme();
            this.applyTheme(savedTheme);

            // Set up toggle button listener when DOM is ready
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.attachToggleListener());
            } else {
                this.attachToggleListener();
            }
        },

        /**
         * Get saved theme from localStorage or default to light theme
         */
        getSavedTheme: function() {
            // Check localStorage first
            const savedTheme = localStorage.getItem(this.STORAGE_KEY);
            if (savedTheme) {
                return savedTheme;
            }

            // Default to light theme
            return this.THEMES.LIGHT;
        },

        /**
         * Apply theme to document
         */
        applyTheme: function(theme) {
            const htmlElement = document.documentElement;
            
            if (theme === this.THEMES.DARK) {
                htmlElement.setAttribute('data-bs-theme', 'dark');
            } else {
                htmlElement.setAttribute('data-bs-theme', 'light');
            }

            // Update toggle button icon if it exists
            this.updateToggleIcon(theme);
        },

        /**
         * Save theme to localStorage
         */
        saveTheme: function(theme) {
            localStorage.setItem(this.STORAGE_KEY, theme);
        },

        /**
         * Toggle between light and dark themes
         */
        toggleTheme: function() {
            const currentTheme = this.getSavedTheme();
            const newTheme = currentTheme === this.THEMES.DARK ? this.THEMES.LIGHT : this.THEMES.DARK;
            
            this.applyTheme(newTheme);
            this.saveTheme(newTheme);

            // Dispatch custom event for other components
            window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: newTheme } }));
        },

        /**
         * Update toggle button icon
         */
        updateToggleIcon: function(theme) {
            const toggleBtn = document.getElementById('themeToggle');
            if (!toggleBtn) return;

            const icon = toggleBtn.querySelector('i');
            if (!icon) return;

            if (theme === this.THEMES.DARK) {
                icon.className = 'fas fa-sun';
                toggleBtn.setAttribute('aria-label', 'Switch to light mode');
                toggleBtn.title = 'Switch to light mode';
            } else {
                icon.className = 'fas fa-moon';
                toggleBtn.setAttribute('aria-label', 'Switch to dark mode');
                toggleBtn.title = 'Switch to dark mode';
            }
        },

        /**
         * Attach click listener to toggle button
         */
        attachToggleListener: function() {
            const toggleBtn = document.getElementById('themeToggle');
            if (!toggleBtn) return;

            toggleBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleTheme();
            });

            // Initialize icon
            const currentTheme = this.getSavedTheme();
            this.updateToggleIcon(currentTheme);
        },

        /**
         * Get current theme
         */
        getCurrentTheme: function() {
            return document.documentElement.getAttribute('data-bs-theme') || this.THEMES.LIGHT;
        }
    };

    // Initialize immediately
    ThemeManager.init();

    // Make ThemeManager globally available
    window.ThemeManager = ThemeManager;

})();