// Course Management Page JavaScript

// Current filter state
let currentFilter = 'active';

document.addEventListener('DOMContentLoaded', function() {
    const menuToggle = document.getElementById('menuToggle');
    const dropdownMenu = document.getElementById('dropdownMenu');
    const closeMenu = document.getElementById('closeMenu');
    
    // Toggle modal
    if (menuToggle && dropdownMenu) {
        menuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            dropdownMenu.style.display = 'flex';
        });
        
        // Close menu button
        if (closeMenu) {
            closeMenu.addEventListener('click', function(e) {
                e.stopPropagation();
                dropdownMenu.style.display = 'none';
            });
        }
        
        // Close modal when clicking on overlay
        dropdownMenu.addEventListener('click', function(e) {
            if (e.target === dropdownMenu || e.target.classList.contains('cm-modal-overlay')) {
                dropdownMenu.style.display = 'none';
            }
        });
        
        // Close modal on Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && dropdownMenu.style.display === 'flex') {
                dropdownMenu.style.display = 'none';
            }
        });
    }
    
    // Apply default filter on page load
    filterCourses('active');
});

// Filter courses by status
function filterCourses(status) {
    currentFilter = status;
    const allCourseItems = document.querySelectorAll('.cm-course-item[data-course-id]');
    let firstVisibleCourse = null;
    
    // Update button states
    const filterAll = document.getElementById('filterAll');
    const filterActive = document.getElementById('filterActive');
    const filterInactive = document.getElementById('filterInactive');
    
    if (filterAll) {
        filterAll.className = status === 'all' ? 'cm-filter-pill cm-filter-pill-active' : 'cm-filter-pill';
    }
    if (filterActive) {
        filterActive.className = status === 'active' ? 'cm-filter-pill cm-filter-pill-active' : 'cm-filter-pill';
    }
    if (filterInactive) {
        filterInactive.className = status === 'inactive' ? 'cm-filter-pill cm-filter-pill-active' : 'cm-filter-pill';
    }
    
    // Filter course items
    allCourseItems.forEach(item => {
        const courseStatus = item.getAttribute('data-status');
        
        if (status === 'all' || courseStatus === status) {
            item.classList.remove('d-none');
            if (!firstVisibleCourse) {
                firstVisibleCourse = item;
            }
        } else {
            item.classList.add('d-none');
        }
    });
    
    // Show the first visible course details
    if (firstVisibleCourse) {
        const courseId = firstVisibleCourse.getAttribute('data-course-id');
        showCourseDetails(courseId);
    } else {
        // Hide all course details if no courses match the filter
        const allDetails = document.querySelectorAll('.cm-detail-card[id^="course-"]');
        allDetails.forEach(detail => {
            detail.classList.add('d-none');
            detail.classList.remove('d-block');
        });
    }
}

// Show course details when clicking on sidebar item
function showCourseDetails(courseId) {
    // Hide all course details
    const allDetails = document.querySelectorAll('.cm-detail-card[id^="course-"]');
    allDetails.forEach(detail => {
        detail.classList.add('d-none');
        detail.classList.remove('d-block');
    });
    
    // Remove active class from all sidebar items
    const allItems = document.querySelectorAll('.cm-course-item[data-course-id]');
    allItems.forEach(item => {
        item.classList.remove('cm-course-item-active');
    });
    
    // Show selected course details
    const selectedDetails = document.getElementById('course-' + courseId);
    if (selectedDetails) {
        selectedDetails.classList.remove('d-none');
        selectedDetails.classList.add('d-block');
    }
    
    // Add active class to clicked sidebar item
    const selectedItem = document.querySelector('.cm-course-item[data-course-id="' + courseId + '"]');
    if (selectedItem) {
        selectedItem.classList.add('cm-course-item-active');
    }
}

// Edit course template
function editCourse(courseId) {
    const detailsBody = document.querySelector('#course-' + courseId + ' .cm-detail-body');
    const editForm = document.getElementById('edit-form-' + courseId);
    
    if (detailsBody && editForm) {
        detailsBody.style.display = 'none';
        editForm.style.display = 'block';
    }
}

// Cancel edit
function cancelEdit(courseId) {
    const detailsBody = document.querySelector('#course-' + courseId + ' .cm-detail-body');
    const editForm = document.getElementById('edit-form-' + courseId);
    
    if (detailsBody && editForm) {
        detailsBody.style.display = 'block';
        editForm.style.display = 'none';
    }
}
