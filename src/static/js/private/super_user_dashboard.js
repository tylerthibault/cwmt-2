/**
 * Super User Dashboard JavaScript
 * Handles interactivity for the super-user dashboard
 */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Super User Dashboard initialized');

    // Initialize components
    initRefreshButton();
    initClearCacheModal();
    initActivityChart();
    initLogAutoRefresh();
});

/**
 * Initialize the refresh stats button
 */
function initRefreshButton() {
    const refreshBtn = document.getElementById('refreshStats');
    
    if (refreshBtn) {
        refreshBtn.addEventListener('click', function(e) {
            e.preventDefault();
            refreshDashboardStats();
        });
    }
}

/**
 * Refresh dashboard statistics
 */
function refreshDashboardStats() {
    const refreshBtn = document.getElementById('refreshStats');
    
    // Add spinning animation
    refreshBtn.disabled = true;
    const icon = refreshBtn.querySelector('i');
    icon.classList.add('fa-spin');
    
    // Simulate API call (replace with actual API endpoint)
    setTimeout(function() {
        // Remove spinning animation
        icon.classList.remove('fa-spin');
        refreshBtn.disabled = false;
        
        // Show success message (you can use your flash message system)
        console.log('Dashboard stats refreshed');
        
        // In a real implementation, you would:
        // 1. Fetch fresh data from the server
        // 2. Update the stat cards with new values
        // 3. Refresh charts and tables
    }, 1000);
}

/**
 * Initialize the clear cache modal
 */
function initClearCacheModal() {
    const confirmBtn = document.getElementById('confirmClearCache');
    
    if (confirmBtn) {
        confirmBtn.addEventListener('click', function() {
            clearSystemCache();
        });
    }
}

/**
 * Clear system cache
 */
function clearSystemCache() {
    const confirmBtn = document.getElementById('confirmClearCache');
    confirmBtn.disabled = true;
    confirmBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Clearing...';
    
    // Simulate cache clearing (replace with actual API endpoint)
    setTimeout(function() {
        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('clearCacheModal'));
        if (modal) {
            modal.hide();
        }
        
        // Reset button
        confirmBtn.disabled = false;
        confirmBtn.innerHTML = '<i class="fas fa-trash"></i> Clear Cache';
        
        // Show success message
        console.log('Cache cleared successfully');
        
        // In a real implementation, you would:
        // 1. Send request to server to clear cache
        // 2. Handle response
        // 3. Show appropriate flash message
        // 4. Optionally refresh the page
    }, 2000);
}

/**
 * Initialize activity chart using Chart.js (if available)
 */
function initActivityChart() {
    const canvas = document.getElementById('activityChart');
    
    if (!canvas) {
        return;
    }
    
    // Check if Chart.js is loaded
    if (typeof Chart === 'undefined') {
        console.warn('Chart.js is not loaded. Activity chart will not be displayed.');
        canvas.parentElement.innerHTML = '<p class="text-muted text-center py-4">Chart library not loaded</p>';
        return;
    }
    
    // Sample data (replace with actual data from server)
    const ctx = canvas.getContext('2d');
    const activityChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'User Logins',
                data: [12, 19, 15, 25, 22, 18, 20],
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.4
            }, {
                label: 'System Events',
                data: [8, 12, 10, 15, 13, 11, 14],
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                },
                title: {
                    display: true,
                    text: 'Last 7 Days Activity'
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Auto-refresh logs every 30 seconds
 */
function initLogAutoRefresh() {
    // Uncomment to enable auto-refresh
    // setInterval(refreshLogs, 30000);
}

/**
 * Refresh system logs
 */
function refreshLogs() {
    const logContainer = document.querySelector('.log-container');
    
    if (!logContainer) {
        return;
    }
    
    // In a real implementation, you would:
    // 1. Fetch fresh logs from the server
    // 2. Update the log container with new entries
    // 3. Maintain scroll position or scroll to latest
    
    console.log('Refreshing logs...');
}

/**
 * Format timestamp for display
 * @param {string} timestamp - ISO timestamp
 * @returns {string} Formatted timestamp
 */
function formatTimestamp(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

/**
 * Show confirmation dialog
 * @param {string} message - Confirmation message
 * @param {Function} callback - Callback function if confirmed
 */
function confirmAction(message, callback) {
    if (confirm(message)) {
        callback();
    }
}

/**
 * Export data to CSV
 * @param {string} dataType - Type of data to export
 */
function exportData(dataType) {
    console.log(`Exporting ${dataType} data...`);
    
    // In a real implementation, you would:
    // 1. Request data from server in CSV format
    // 2. Create a download link
    // 3. Trigger download
}

// Export functions for use in HTML onclick attributes if needed
window.dashboardUtils = {
    refreshStats: refreshDashboardStats,
    clearCache: clearSystemCache,
    refreshLogs: refreshLogs,
    exportData: exportData
};
