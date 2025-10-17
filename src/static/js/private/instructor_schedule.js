/**
 * Instructor Schedule Management
 * Handles course filtering, sign-up, and removal functionality
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Instructor schedule page loaded');
    // Apply initial filter (available courses)
    filterByStatus('available');
});

/**
 * Filter courses by status
 * @param {string} status - Status to filter by (all, available, my-courses, full)
 */
function filterByStatus(status) {
    const cards = document.querySelectorAll('.course-card');
    
    cards.forEach(card => {
        const cardStatus = card.getAttribute('data-status');
        
        if (status === 'all') {
            card.style.display = '';
        } else if (status === 'available' && cardStatus !== 'full' && cardStatus !== 'my-courses') {
            card.style.display = '';
        } else if (status === cardStatus) {
            card.style.display = '';
        } else {
            card.style.display = 'none';
        }
    });
    
    // Update count
    updateVisibleCount();
}

/**
 * Filter courses by date range
 * @param {string} range - Range to filter by (week, month, all)
 */
function filterByDate(range) {
    const cards = document.querySelectorAll('.course-card');
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    
    let endDate = new Date(today);
    
    if (range === 'week') {
        endDate.setDate(today.getDate() + 7);
    } else if (range === 'month') {
        endDate.setDate(today.getDate() + 30);
    } else {
        // Show all - no date filtering
        cards.forEach(card => {
            if (card.style.display !== 'none') {
                card.style.display = '';
            }
        });
        updateVisibleCount();
        return;
    }
    
    cards.forEach(card => {
        const cardDateStr = card.getAttribute('data-date');
        const cardDate = new Date(cardDateStr);
        
        if (cardDate >= today && cardDate <= endDate) {
            // Don't change display if already hidden by status filter
            if (card.style.display !== 'none') {
                card.style.display = '';
            }
        } else {
            card.style.display = 'none';
        }
    });
    
    updateVisibleCount();
}

/**
 * Update the count of visible courses
 */
function updateVisibleCount() {
    const visibleCards = document.querySelectorAll('.course-card:not([style*="display: none"])');
    const totalCards = document.querySelectorAll('.course-card');
    
    console.log(`Showing ${visibleCards.length} of ${totalCards.length} courses`);
}

/**
 * Sign up for a course as an instructor
 * @param {number} courseId - ID of the course to sign up for
 */
function signUpForCourse(courseId) {
    if (!confirm('Are you sure you want to sign up for this course?')) {
        return;
    }
    
    // Show loading state
    const button = event.target.closest('button');
    const originalContent = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Signing up...';
    
    fetch(`/instructor/schedule/signup/${courseId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => Promise.reject(err));
        }
        return response.json();
    })
    .then(data => {
        // Success - reload page to show updated assignments
        window.location.reload();
    })
    .catch(error => {
        console.error('Error signing up for course:', error);
        alert(error.message || 'Failed to sign up for course. Please try again.');
        
        // Restore button state
        button.disabled = false;
        button.innerHTML = originalContent;
    });
}

/**
 * Remove self from a course
 * @param {number} courseId - ID of the course to remove from
 */
function removeFromCourse(courseId) {
    if (!confirm('Are you sure you want to remove yourself from this course?')) {
        return;
    }
    
    // Show loading state
    const button = event.target.closest('button');
    const originalContent = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Removing...';
    
    fetch(`/instructor/schedule/remove/${courseId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => Promise.reject(err));
        }
        return response.json();
    })
    .then(data => {
        // Success - reload page to show updated assignments
        window.location.reload();
    })
    .catch(error => {
        console.error('Error removing from course:', error);
        alert(error.message || 'Failed to remove from course. Please try again.');
        
        // Restore button state
        button.disabled = false;
        button.innerHTML = originalContent;
    });
}
