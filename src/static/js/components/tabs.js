/**
 * Enhanced Tab Component with State Persistence
 * 
 * Features:
 * - Remembers active tab on page refresh using localStorage
 * - Supports custom callbacks for tab changes
 * - Handles URL hash navigation
 * - Bootstrap 5 compatible
 * - Event-driven architecture
 */

class TabManager {
    constructor(options = {}) {
        this.options = {
            storageKey: 'activeTab',
            useUrlHash: true,
            autoInit: true,
            onTabChange: null,
            onTabShow: null,
            onTabHide: null,
            ...options
        };

        this.activeTab = null;
        this.tabs = new Map();
        this.tabContainers = [];

        if (this.options.autoInit) {
            this.init();
        }
    }

    /**
     * Initialize the tab manager
     */
    init() {
        this.findTabContainers();
        this.bindEvents();
        this.restoreActiveTab();
    }

    /**
     * Find and register all tab containers on the page
     */
    findTabContainers() {
        const containers = document.querySelectorAll('[data-tab-container]');
        
        containers.forEach(container => {
            const containerId = container.getAttribute('data-tab-container') || 
                               container.id || 
                               `tab-container-${Math.random().toString(36).substr(2, 9)}`;
            
            this.registerTabContainer(containerId, container);
        });
    }

    /**
     * Register a tab container
     */
    registerTabContainer(containerId, container) {
        if (this.tabContainers.find(tc => tc.id === containerId)) {
            console.warn(`Tab container with ID ${containerId} already registered`);
            return;
        }

        const tabButtons = container.querySelectorAll('[data-bs-toggle="pill"], [data-bs-toggle="tab"]');
        const tabPanes = container.querySelectorAll('.tab-pane');

        const containerData = {
            id: containerId,
            element: container,
            buttons: Array.from(tabButtons),
            panes: Array.from(tabPanes),
            storageKey: `${this.options.storageKey}_${containerId}`
        };

        this.tabContainers.push(containerData);

        // Register individual tabs
        tabButtons.forEach(button => {
            const tabId = this.getTabId(button);
            const pane = this.getTabPane(button);
            
            if (tabId && pane) {
                this.tabs.set(tabId, {
                    button,
                    pane,
                    containerId,
                    id: tabId
                });
            }
        });
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Listen for Bootstrap tab events
        document.addEventListener('show.bs.tab', (e) => this.handleTabShow(e));
        document.addEventListener('shown.bs.tab', (e) => this.handleTabShown(e));
        document.addEventListener('hide.bs.tab', (e) => this.handleTabHide(e));

        // Listen for hash changes
        if (this.options.useUrlHash) {
            window.addEventListener('hashchange', () => this.handleHashChange());
        }

        // Listen for storage changes (for cross-tab synchronization)
        window.addEventListener('storage', (e) => this.handleStorageChange(e));
    }

    /**
     * Handle tab show event (before showing)
     */
    handleTabShow(event) {
        const tabId = this.getTabId(event.target);
        const containerId = this.getContainerId(event.target);

        if (this.options.onTabShow) {
            this.options.onTabShow(tabId, event.target, containerId);
        }
    }

    /**
     * Handle tab shown event (after showing)
     */
    handleTabShown(event) {
        const tabId = this.getTabId(event.target);
        const containerId = this.getContainerId(event.target);

        this.activeTab = tabId;
        this.saveActiveTab(containerId, tabId);

        if (this.options.useUrlHash && tabId) {
            this.updateUrlHash(tabId);
        }

        if (this.options.onTabChange) {
            this.options.onTabChange(tabId, event.target, containerId);
        }

        // Dispatch custom event
        this.dispatchTabEvent('tabChanged', { tabId, containerId, button: event.target });
    }

    /**
     * Handle tab hide event
     */
    handleTabHide(event) {
        const tabId = this.getTabId(event.target);
        const containerId = this.getContainerId(event.target);

        if (this.options.onTabHide) {
            this.options.onTabHide(tabId, event.target, containerId);
        }
    }

    /**
     * Handle URL hash changes
     */
    handleHashChange() {
        const hash = window.location.hash.substring(1);
        if (hash && this.tabs.has(hash)) {
            this.showTab(hash);
        }
    }

    /**
     * Handle localStorage changes (cross-tab sync)
     */
    handleStorageChange(event) {
        if (event.key && event.key.startsWith(this.options.storageKey)) {
            const containerId = event.key.replace(`${this.options.storageKey}_`, '');
            const tabId = event.newValue;
            
            if (tabId && this.tabs.has(tabId)) {
                this.showTab(tabId);
            }
        }
    }

    /**
     * Show a specific tab
     */
    showTab(tabId) {
        const tab = this.tabs.get(tabId);
        if (!tab) {
            console.warn(`Tab with ID ${tabId} not found`);
            return false;
        }

        // Use Bootstrap's tab method
        const tabInstance = bootstrap.Tab.getOrCreateInstance(tab.button);
        tabInstance.show();
        return true;
    }

    /**
     * Get the currently active tab for a container
     */
    getActiveTab(containerId = null) {
        if (containerId) {
            const container = this.tabContainers.find(tc => tc.id === containerId);
            if (container) {
                const activeButton = container.element.querySelector('.nav-link.active, .btn.active');
                return activeButton ? this.getTabId(activeButton) : null;
            }
        }
        return this.activeTab;
    }

    /**
     * Save active tab to localStorage
     */
    saveActiveTab(containerId, tabId) {
        const storageKey = `${this.options.storageKey}_${containerId}`;
        try {
            localStorage.setItem(storageKey, tabId);
        } catch (e) {
            console.warn('Could not save tab state to localStorage:', e);
        }
    }

    /**
     * Restore active tab from localStorage or URL hash
     */
    restoreActiveTab() {
        // Check URL hash first
        const hash = window.location.hash.substring(1);
        if (hash && this.tabs.has(hash)) {
            this.showTab(hash);
            return;
        }

        // Restore from localStorage for each container
        this.tabContainers.forEach(container => {
            const storageKey = `${this.options.storageKey}_${container.id}`;
            try {
                const savedTabId = localStorage.getItem(storageKey);
                if (savedTabId && this.tabs.has(savedTabId)) {
                    const tab = this.tabs.get(savedTabId);
                    if (tab.containerId === container.id) {
                        this.showTab(savedTabId);
                    }
                }
            } catch (e) {
                console.warn('Could not restore tab state from localStorage:', e);
            }
        });
    }

    /**
     * Update URL hash
     */
    updateUrlHash(tabId) {
        if (history.replaceState) {
            history.replaceState(null, null, `#${tabId}`);
        } else {
            window.location.hash = tabId;
        }
    }

    /**
     * Get tab ID from button element
     */
    getTabId(button) {
        // Try data-tab-id first, then target, then href
        return button.getAttribute('data-tab-id') ||
               button.getAttribute('data-bs-target')?.substring(1) ||
               button.getAttribute('href')?.substring(1) ||
               button.id;
    }

    /**
     * Get container ID for a tab button
     */
    getContainerId(button) {
        const container = button.closest('[data-tab-container]');
        return container ? 
               (container.getAttribute('data-tab-container') || container.id) : 
               'default';
    }

    /**
     * Get tab pane element
     */
    getTabPane(button) {
        const target = button.getAttribute('data-bs-target') || button.getAttribute('href');
        return target ? document.querySelector(target) : null;
    }

    /**
     * Dispatch custom tab events
     */
    dispatchTabEvent(eventName, detail) {
        const event = new CustomEvent(eventName, { 
            detail,
            bubbles: true,
            cancelable: true 
        });
        document.dispatchEvent(event);
    }

    /**
     * Clear saved tab states
     */
    clearSavedStates() {
        this.tabContainers.forEach(container => {
            const storageKey = `${this.options.storageKey}_${container.id}`;
            try {
                localStorage.removeItem(storageKey);
            } catch (e) {
                console.warn('Could not clear tab state from localStorage:', e);
            }
        });
    }

    /**
     * Destroy the tab manager
     */
    destroy() {
        // Remove event listeners
        document.removeEventListener('show.bs.tab', this.handleTabShow);
        document.removeEventListener('shown.bs.tab', this.handleTabShown);
        document.removeEventListener('hide.bs.tab', this.handleTabHide);
        
        if (this.options.useUrlHash) {
            window.removeEventListener('hashchange', this.handleHashChange);
        }
        
        window.removeEventListener('storage', this.handleStorageChange);

        // Clear data
        this.tabs.clear();
        this.tabContainers = [];
        this.activeTab = null;
    }
}

// Auto-initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize global tab manager
    window.tabManager = new TabManager();
    
    // Expose TabManager class for manual instantiation
    window.TabManager = TabManager;
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = TabManager;
}