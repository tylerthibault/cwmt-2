/**
 * Announcements Dashboard JavaScript
 * Handles announcement CRUD operations, filtering, and modal interactions
 */

document.addEventListener('DOMContentLoaded', function() {
    initializeAnnouncementButtons();
    initializeFilters();
    initializeStatusChange();
    initializeDeleteButtons();
});

/**
 * Initialize announcement creation and edit buttons
 */
function initializeAnnouncementButtons() {
    const createBtn = document.getElementById('createAnnouncementBtn');
    const createFirstBtn = document.getElementById('createFirstAnnouncementBtn');
    const editButtons = document.querySelectorAll('.action-btn--edit');
    
    if (createBtn) {
        createBtn.addEventListener('click', () => openAnnouncementModal('create'));
    }
    
    if (createFirstBtn) {
        createFirstBtn.addEventListener('click', () => openAnnouncementModal('create'));
    }
    
    editButtons.forEach(button => {
        button.addEventListener('click', handleEditClick);
    });
}

/**
 * Open announcement modal for create or edit
 */
function openAnnouncementModal(mode, announcementId = null) {
    const modal = document.getElementById('announcementModal');
    const modalTitle = document.getElementById('announcementModalLabel');
    const form = document.getElementById('announcementForm');
    const submitBtn = document.getElementById('submitAnnouncementBtn');
    
    if (mode === 'create') {
        modalTitle.textContent = 'Create Announcement';
        submitBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
                <polyline points="17 21 17 13 7 13 7 21"></polyline>
                <polyline points="7 3 7 8 15 8"></polyline>
            </svg>
            Create Announcement
        `;
        form.action = '/admin/announcements/create';
        form.reset();
    } else if (mode === 'edit') {
        modalTitle.textContent = 'Edit Announcement';
        submitBtn.innerHTML = `
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path>
                <polyline points="17 21 17 13 7 13 7 21"></polyline>
                <polyline points="7 3 7 8 15 8"></polyline>
            </svg>
            Update Announcement
        `;
        form.action = `/admin/announcements/edit/${announcementId}`;
        
        // TODO: Fetch and populate announcement data
        // This would typically involve an AJAX call to get the announcement details
        fetchAnnouncementData(announcementId);
    }
    
    // Show modal using Bootstrap
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

/**
 * Handle edit button click
 */
function handleEditClick(event) {
    const announcementId = event.currentTarget.dataset.announcementId;
    openAnnouncementModal('edit', announcementId);
}

/**
 * Fetch announcement data for editing
 */
function fetchAnnouncementData(announcementId) {
    // This would be implemented when the backend API is ready
    console.log(`Fetching announcement data for ID: ${announcementId}`);
    
    // Example implementation:
    // fetch(`/api/announcements/${announcementId}`)
    //     .then(response => response.json())
    //     .then(data => populateAnnouncementForm(data))
    //     .catch(error => console.error('Error fetching announcement:', error));
}

/**
 * Populate announcement form with data
 */
function populateAnnouncementForm(data) {
    document.getElementById('announcementId').value = data.id;
    document.getElementById('announcementTitle').value = data.title;
    document.getElementById('announcementContent').value = data.content;
    document.getElementById('announcementPriority').value = data.priority;
    document.getElementById('announcementAudience').value = data.audience;
    document.getElementById('announcementStatus').value = data.status;
    
    if (data.scheduled_for) {
        // Convert datetime to input format (YYYY-MM-DDTHH:MM)
        const scheduledDate = new Date(data.scheduled_for);
        const formattedDate = formatDateTimeLocal(scheduledDate);
        document.getElementById('scheduledFor').value = formattedDate;
    }
    
    document.getElementById('sendNotification').checked = data.send_notification || false;
    document.getElementById('pinAnnouncement').checked = data.pinned || false;
}

/**
 * Format date for datetime-local input
 */
function formatDateTimeLocal(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    
    return `${year}-${month}-${day}T${hours}:${minutes}`;
}

/**
 * Initialize filter functionality
 */
function initializeFilters() {
    const statusFilter = document.getElementById('statusFilter');
    const priorityFilter = document.getElementById('priorityFilter');
    const audienceFilter = document.getElementById('audienceFilter');
    const searchInput = document.getElementById('searchInput');
    
    if (statusFilter) {
        statusFilter.addEventListener('change', applyFilters);
    }
    
    if (priorityFilter) {
        priorityFilter.addEventListener('change', applyFilters);
    }
    
    if (audienceFilter) {
        audienceFilter.addEventListener('change', applyFilters);
    }
    
    if (searchInput) {
        searchInput.addEventListener('input', debounce(applyFilters, 300));
    }
}

/**
 * Apply filters to announcement cards
 */
function applyFilters() {
    const statusFilter = document.getElementById('statusFilter').value.toLowerCase();
    const priorityFilter = document.getElementById('priorityFilter').value.toLowerCase();
    const audienceFilter = document.getElementById('audienceFilter').value.toLowerCase();
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    
    const announcementCards = document.querySelectorAll('.announcement-card');
    let visibleCount = 0;
    
    announcementCards.forEach(card => {
        const status = card.dataset.status.toLowerCase();
        const priority = card.dataset.priority.toLowerCase();
        const audience = card.dataset.audience.toLowerCase();
        const title = card.querySelector('.announcement-title').textContent.toLowerCase();
        const body = card.querySelector('.announcement-body').textContent.toLowerCase();
        
        const matchesStatus = !statusFilter || status === statusFilter;
        const matchesPriority = !priorityFilter || priority === priorityFilter;
        const matchesAudience = !audienceFilter || audience === audienceFilter;
        const matchesSearch = !searchTerm || title.includes(searchTerm) || body.includes(searchTerm);
        
        if (matchesStatus && matchesPriority && matchesAudience && matchesSearch) {
            card.style.display = '';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });
    
    // Show/hide empty state if needed
    const emptyState = document.querySelector('.empty-state');
    if (emptyState) {
        emptyState.style.display = visibleCount === 0 ? 'flex' : 'none';
    }
}

/**
 * Debounce function for search input
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Initialize status change dropdown
 */
function initializeStatusChange() {
    const statusSelects = document.querySelectorAll('.status-select');
    
    statusSelects.forEach(select => {
        select.addEventListener('change', handleStatusChange);
    });
}

/**
 * Handle announcement status change
 */
function handleStatusChange(event) {
    const announcementId = event.target.dataset.announcementId;
    const newStatus = event.target.value;
    
    // Show confirmation for certain status changes
    if (newStatus === 'archived') {
        if (!confirm('Are you sure you want to archive this announcement?')) {
            event.target.value = event.target.dataset.originalValue;
            return;
        }
    }
    
    updateAnnouncementStatus(announcementId, newStatus);
}

/**
 * Update announcement status via API
 */
function updateAnnouncementStatus(announcementId, status) {
    // This would be implemented when the backend API is ready
    console.log(`Updating announcement ${announcementId} to status: ${status}`);
    
    // Example implementation:
    // fetch(`/api/announcements/${announcementId}/status`, {
    //     method: 'PATCH',
    //     headers: {
    //         'Content-Type': 'application/json',
    //     },
    //     body: JSON.stringify({ status: status })
    // })
    // .then(response => response.json())
    // .then(data => {
    //     showAlert('Status updated successfully', 'success');
    //     // Refresh or update UI
    // })
    // .catch(error => {
    //     showAlert('Error updating status', 'danger');
    //     console.error('Error:', error);
    // });
}

/**
 * Initialize delete buttons
 */
function initializeDeleteButtons() {
    const deleteButtons = document.querySelectorAll('.action-btn--delete');
    
    deleteButtons.forEach(button => {
        button.addEventListener('click', handleDeleteClick);
    });
}

/**
 * Handle delete button click
 */
function handleDeleteClick(event) {
    const announcementId = event.currentTarget.dataset.announcementId;
    openDeleteModal(announcementId);
}

/**
 * Open delete confirmation modal
 */
function openDeleteModal(announcementId) {
    const modal = document.getElementById('deleteModal');
    const deleteForm = document.getElementById('deleteForm');
    
    deleteForm.action = `/admin/announcements/delete/${announcementId}`;
    
    // Show modal using Bootstrap
    const bsModal = new bootstrap.Modal(modal);
    bsModal.show();
}

/**
 * Show alert message (placeholder for flash message system)
 */
function showAlert(message, type = 'info') {
    console.log(`Alert (${type}): ${message}`);
    
    // This would integrate with the existing flash message system
    // For now, using a simple console log
}

/**
 * Validate announcement form before submission
 */
function validateAnnouncementForm() {
    const title = document.getElementById('announcementTitle').value.trim();
    const content = document.getElementById('announcementContent').value.trim();
    const status = document.getElementById('announcementStatus').value;
    const scheduledFor = document.getElementById('scheduledFor').value;
    
    if (!title) {
        showAlert('Please enter a title', 'warning');
        return false;
    }
    
    if (!content) {
        showAlert('Please enter content', 'warning');
        return false;
    }
    
    if (status === 'scheduled' && !scheduledFor) {
        showAlert('Please select a scheduled date and time', 'warning');
        return false;
    }
    
    if (scheduledFor) {
        const scheduledDate = new Date(scheduledFor);
        const now = new Date();
        
        if (scheduledDate <= now) {
            showAlert('Scheduled date must be in the future', 'warning');
            return false;
        }
    }
    
    return true;
}

/**
 * Form submission handler
 */
document.getElementById('announcementForm')?.addEventListener('submit', function(event) {
    if (!validateAnnouncementForm()) {
        event.preventDefault();
    }
});

/**
 * Auto-update status select when scheduled date is set
 */
document.getElementById('scheduledFor')?.addEventListener('change', function() {
    const statusSelect = document.getElementById('announcementStatus');
    
    if (this.value && statusSelect.value !== 'scheduled') {
        if (confirm('Would you like to set the status to "Scheduled"?')) {
            statusSelect.value = 'scheduled';
        }
    }
});

/**
 * Clear scheduled date when status is not scheduled
 */
document.getElementById('announcementStatus')?.addEventListener('change', function() {
    const scheduledForInput = document.getElementById('scheduledFor');
    
    if (this.value !== 'scheduled' && scheduledForInput.value) {
        if (confirm('Status is not "Scheduled". Clear the scheduled date?')) {
            scheduledForInput.value = '';
        }
    }
});
