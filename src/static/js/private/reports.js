/**
 * Reports Dashboard JavaScript
 * Handles report generation modal and form submission
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeReportButtons();
    initializeReportForm();
});

/**
 * Initialize report generation buttons
 */
function initializeReportButtons() {
    const reportButtons = document.querySelectorAll('.generate-report-btn');
    
    reportButtons.forEach(button => {
        button.addEventListener('click', handleReportButtonClick);
    });
}

/**
 * Handle report button click
 * Opens modal with pre-filled report type
 */
function handleReportButtonClick(event) {
    event.preventDefault();
    
    const button = event.currentTarget;
    const reportType = button.dataset.reportType;
    const reportName = button.dataset.reportName;
    
    openReportModal(reportType, reportName);
}

/**
 * Open report generation modal
 */
function openReportModal(reportType, reportName) {
    const modal = document.getElementById('reportModal');
    const reportTypeInput = document.getElementById('reportType');
    const reportDescription = document.getElementById('reportDescription');
    const modalTitle = document.getElementById('reportModalLabel');
    
    // Set report type
    reportTypeInput.value = reportType;
    
    // Update modal title
    modalTitle.textContent = `Generate ${reportName} Report`;
    
    // Update description based on report type
    const descriptions = {
        enrollment: 'Select a date range to analyze course enrollment statistics and trends.',
        attendance: 'Choose the time period to review attendance patterns and participation rates.',
        completion: 'Define the date range to examine course completion rates and success metrics.',
        instructor: 'Select dates to evaluate instructor performance and teaching effectiveness.',
        popularity: 'Pick a time frame to discover trending courses and enrollment patterns.',
        revenue: 'Choose a period to analyze revenue streams and financial performance.'
    };
    
    reportDescription.textContent = descriptions[reportType] || 'Configure your report parameters below.';
    
    // Set default date range (last 30 days)
    setDefaultDateRange();
    
    // Show modal using Bootstrap
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

/**
 * Set default date range to last 30 days
 */
function setDefaultDateRange() {
    const dateFrom = document.getElementById('dateFrom');
    const dateTo = document.getElementById('dateTo');
    
    const today = new Date();
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(today.getDate() - 30);
    
    dateFrom.value = formatDate(thirtyDaysAgo);
    dateTo.value = formatDate(today);
}

/**
 * Format date as YYYY-MM-DD
 */
function formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    
    return `${year}-${month}-${day}`;
}

/**
 * Initialize report form submission
 */
function initializeReportForm() {
    const reportForm = document.getElementById('reportForm');
    
    if (reportForm) {
        reportForm.addEventListener('submit', handleReportFormSubmit);
    }
}

/**
 * Handle report form submission
 */
function handleReportFormSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    const reportType = formData.get('report_type');
    
    // Validate date range
    if (!validateDateRange(formData)) {
        showAlert('Please select a valid date range.', 'warning');
        return;
    }
    
    // Build query string
    const queryParams = new URLSearchParams(formData).toString();
    
    // Determine URL based on report type
    const reportUrls = {
        enrollment: '/admin/reports/course-enrollment',
        attendance: '/admin/reports/attendance',
        completion: '/admin/reports/completion',
        instructor: '/admin/reports/instructor',
        popularity: '/admin/reports/popularity',
        revenue: '/admin/reports/revenue'
    };
    
    const url = reportUrls[reportType];
    
    if (!url) {
        showAlert('Invalid report type selected.', 'danger');
        return;
    }
    
    // Redirect to report page with parameters
    window.location.href = `${url}?${queryParams}`;
}

/**
 * Validate date range
 */
function validateDateRange(formData) {
    const dateFrom = formData.get('date_from');
    const dateTo = formData.get('date_to');
    
    if (!dateFrom || !dateTo) {
        return false;
    }
    
    const fromDate = new Date(dateFrom);
    const toDate = new Date(dateTo);
    
    if (fromDate > toDate) {
        showAlert('Start date must be before end date.', 'warning');
        return false;
    }
    
    return true;
}

/**
 * Show alert message
 */
function showAlert(message, type = 'info') {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.setAttribute('role', 'alert');
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Insert at top of modal body
    const modalBody = document.querySelector('.modal-body');
    modalBody.insertBefore(alert, modalBody.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

/**
 * Export report functionality (placeholder)
 */
function exportReport(format) {
    console.log(`Exporting report as ${format}`);
    
    // This would be implemented based on backend API
    showAlert(`Export as ${format} is not yet implemented.`, 'info');
}

/**
 * Print report functionality
 */
function printReport() {
    window.print();
}
